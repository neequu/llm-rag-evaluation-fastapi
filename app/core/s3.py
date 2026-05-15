from contextlib import asynccontextmanager
from typing import BinaryIO
from uuid import uuid4

import aioboto3
from botocore.exceptions import ClientError

from app.core.config import settings


class S3Client:
    def __init__(self) -> None:
        self._session = aioboto3.Session()

    @asynccontextmanager
    async def _client(self):
        """Raw async boto3 client. Internal use only — callers use the helpers."""
        async with self._session.client(
            "s3",
            endpoint_url=settings.MINIO_URL,
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            region_name="us-east-1",
        ) as client:
            yield client

    async def ensure_bucket(self, bucket: str | None = None) -> None:
        """Create the bucket if it doesn't already exist.

        Called from FastAPI lifespan so the bucket is ready before the first
        request. Safe to call multiple times — it's idempotent.
        """
        bucket = bucket or settings.MINIO_BUCKET_NAME
        async with self._client() as client:
            try:
                await client.head_bucket(Bucket=bucket)
            except ClientError as exc:
                error_code = exc.response["Error"]["Code"]
                if error_code in ("404", "NoSuchBucket"):
                    await client.create_bucket(Bucket=bucket)
                else:
                    raise

    async def upload_file(
        self,
        file_obj: BinaryIO,
        object_key: str | None = None,
        content_type: str = "application/octet-stream",
        bucket: str | None = None,
        extra_metadata: dict[str, str] | None = None,
    ) -> str:
        """Upload a file-like object and return the object key.

        We auto-generate a UUID key if none is provided. This avoids filename
        collisions and prevents users from overwriting each other's files by
        guessing a predictable path.

        Args:
            file_obj: Any file-like object with a .read() method.
            object_key: S3 key (path). Auto-generated if omitted.
            content_type: MIME type stored as S3 metadata.
            bucket: Override the default bucket.
            extra_metadata: Arbitrary string key-value pairs stored as S3
                user-defined metadata (accessible without downloading the file).

        Returns:
            The object key (not a full URL — use get_presigned_url for that).
        """
        bucket = bucket or settings.MINIO_BUCKET_NAME
        key = object_key or str(uuid4())
        metadata = extra_metadata or {}

        async with self._client() as client:
            await client.upload_fileobj(
                file_obj,
                bucket,
                key,
                ExtraArgs={
                    "ContentType": content_type,
                    "Metadata": metadata,
                },
            )
        return key

    async def get_presigned_url(
        self,
        object_key: str,
        expires_in: int = 3600,
        bucket: str | None = None,
    ) -> str:
        """Generate a time-limited presigned GET URL.

        Why presigned URLs instead of streaming through FastAPI?
        - The client downloads directly from MinIO — zero load on your app server.
        - No need to hold a DB/app connection open for the duration of the download.
        - Works for arbitrarily large files without buffering in memory.

        Args:
            object_key: The S3 key returned by upload_file.
            expires_in: Seconds until the URL expires (default 1 hour).
            bucket: Override the default bucket.

        Returns:
            A short-lived HTTPS URL the client can use directly.
        """
        bucket = bucket or settings.MINIO_BUCKET_NAME
        async with self._client() as client:
            url = await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": bucket, "Key": object_key},
                ExpiresIn=expires_in,
            )
        return url

    async def get_presigned_upload_url(
        self,
        object_key: str | None = None,
        expires_in: int = 900,
        content_type: str = "application/octet-stream",
        bucket: str | None = None,
    ) -> tuple[str, str]:
        """Generate a presigned PUT URL for direct client-to-S3 uploads.

        This is the pattern for large file uploads: the client uploads directly
        to MinIO, bypassing your API server entirely. Your server only issues
        the presigned URL and later receives a webhook/callback to record the
        upload in your DB.

        Returns:
            A tuple of (object_key, presigned_put_url).
        """
        bucket = bucket or settings.MINIO_BUCKET_NAME
        key = object_key or str(uuid4())
        async with self._client() as client:
            url = await client.generate_presigned_url(
                "put_object",
                Params={
                    "Bucket": bucket,
                    "Key": key,
                    "ContentType": content_type,
                },
                ExpiresIn=expires_in,
            )
        return key, url

    async def delete_file(
        self,
        object_key: str,
        bucket: str | None = None,
    ) -> None:
        """Delete an object from S3. Idempotent — deleting a non-existent key
        does not raise an error (S3 semantics)."""
        bucket = bucket or settings.MINIO_BUCKET_NAME
        async with self._client() as client:
            await client.delete_object(Bucket=bucket, Key=object_key)

    async def delete_many(
        self,
        object_keys: list[str],
        bucket: str | None = None,
    ) -> None:
        """Batch-delete up to 1000 objects in a single API call.
        More efficient than calling delete_file in a loop."""
        bucket = bucket or settings.MINIO_BUCKET_NAME
        if not object_keys:
            return
        objects = [{"Key": k} for k in object_keys]
        async with self._client() as client:
            await client.delete_objects(
                Bucket=bucket,
                Delete={"Objects": objects, "Quiet": True},
            )

    async def object_exists(
        self,
        object_key: str,
        bucket: str | None = None,
    ) -> bool:
        """Return True if the object exists in S3."""
        bucket = bucket or settings.MINIO_BUCKET_NAME
        async with self._client() as client:
            try:
                await client.head_object(Bucket=bucket, Key=object_key)
                return True
            except ClientError as exc:
                if exc.response["Error"]["Code"] == "404":
                    return False
                raise


s3_client = S3Client()
