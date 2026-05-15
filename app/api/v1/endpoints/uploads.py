import logging
from typing import Annotated

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status

from app.core.s3 import s3_client
from app.schemas.uploads import (
    DownloadResponse,
    PresignedUploadResponse,
    UploadResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/files", tags=["files"])


ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "application/pdf",
    "text/plain",
    "text/csv",
}

MAX_FILE_SIZE = 100 * 1024 * 1024


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post(
    "/upload", response_model=UploadResponse, status_code=status.HTTP_202_ACCEPTED
)
async def upload_file(
    file: Annotated[UploadFile, File(description="File to upload")],
    user_id: str = Query(..., description="ID of the uploading user"),
):
    """
    Server-side upload: the API receives the file bytes and streams them to S3.

    Use this for small files (< ~10MB) or when you need to inspect the file
    content on the server (e.g. virus scan, content extraction) before storing.

    Returns 202 Accepted because processing is async — the file is stored
    immediately but background work (indexing, thumbnailing, etc.) is queued.
    """
    # 1. Validate content type
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Content type {file.content_type!r} is not allowed. "
            f"Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    # 2. Stream to S3 — UploadFile.file is a SpooledTemporaryFile which
    #    implements the BinaryIO interface, so we can pass it directly.
    #    No need to read all bytes into memory first.
    object_key = await s3_client.upload_file(
        file_obj=file.file,
        content_type=file.content_type or "application/octet-stream",
        extra_metadata={
            "original_filename": file.filename or "unknown",
            "user_id": user_id,
        },
    )

    logger.info(
        "File uploaded to S3",
        extra={"object_key": object_key, "filename": file.filename, "user_id": user_id},
    )

    return UploadResponse(
        object_key=object_key,
        file_name=file.filename or "unknown",
        content_type=file.content_type or "application/octet-stream",
        task_id="",
    )


@router.post(
    "/presigned-upload",
    response_model=PresignedUploadResponse,
    status_code=status.HTTP_200_OK,
)
async def get_presigned_upload_url(
    content_type: str = Query(
        default="application/octet-stream",
        description="MIME type of the file you will upload",
    ),
    expires_in: int = Query(default=900, ge=60, le=3600),
):
    """
    Issue a presigned S3 PUT URL for direct client-to-MinIO upload.

    Workflow:
    1. Client calls this endpoint to get a presigned URL and an object_key.
    2. Client PUTs the file directly to the presigned URL (Content-Type header
       MUST match what was specified here).
    3. Client calls POST /files/confirm-upload with the object_key so the API
       can record it in the DB and enqueue processing tasks.

    This pattern scales better for large files because:
    - No API memory pressure (bytes never touch the API server).
    - No API connection held open for the duration of a slow upload.
    - MinIO handles multipart upload resumption automatically.
    """
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Content type {content_type!r} is not allowed.",
        )

    object_key, upload_url = await s3_client.get_presigned_upload_url(
        content_type=content_type,
        expires_in=expires_in,
    )

    return PresignedUploadResponse(
        object_key=object_key,
        upload_url=upload_url,
        expires_in=expires_in,
    )


@router.get("/download/{object_key:path}", response_model=DownloadResponse)
async def get_download_url(
    object_key: str,
    expires_in: int = Query(default=3600, ge=60, le=86400),
):
    """
    Generate a presigned GET URL for downloading a file.

    The {object_key:path} path converter allows slashes in the key
    (e.g. "users/abc/2024/document.pdf").
    """
    exists = await s3_client.object_exists(object_key)
    if not exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"File {object_key!r} not found.",
        )

    url = await s3_client.get_presigned_url(object_key, expires_in=expires_in)
    return DownloadResponse(download_url=url, expires_in=expires_in)


@router.delete("/{object_key:path}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_file(object_key: str):
    """
    Delete a file from S3. Returns 204 even if the file didn't exist
    (S3 delete is idempotent by specification).
    """
    await s3_client.delete_file(object_key)
    logger.info("File deleted", extra={"object_key": object_key})
