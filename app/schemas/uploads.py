from pydantic import BaseModel


class UploadResponse(BaseModel):
    object_key: str
    file_name: str
    content_type: str
    task_id: str
    message: str = "File uploaded. Processing has been queued."


class PresignedUploadResponse(BaseModel):
    object_key: str
    upload_url: str
    expires_in: int
    message: str = (
        "PUT the file directly to upload_url. Content-Type header must match."
    )


class DownloadResponse(BaseModel):
    download_url: str
    expires_in: int
