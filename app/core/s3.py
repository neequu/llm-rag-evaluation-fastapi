from contextlib import asynccontextmanager

import aioboto3

from app.core.config import settings


class S3Client:
    def __init__(self):
        self.session = aioboto3.Session()

        self.endpoint_url = (
            f"http://{self.settings.MINIO_HOST}:{self.settings.MINIO_API_PORT}"
        )
        self.access_key = settings.MINIO_ROOT_USER
        self.secret_key = settings.MINIO_ROOT_PASSWORD
        self.bucket_name = settings.MINIO_BUCKET_NAME
        self.use_ssl = settings.MINIO_SECURE

    @asynccontextmanager
    async def get_client(self):
        async with self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl=self.use_ssl,
        ) as client:
            yield client


s3 = S3Client()
