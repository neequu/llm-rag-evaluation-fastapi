from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from ..models.document import DocumentState


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    filename: str
    content_type: str
    file_size: int
    status: DocumentState
    workspace_id: UUID
    uploader_id: UUID
    created_at: datetime


class DocumentCreate(BaseModel):
    filename: str
    content_type: str
    file_size: int
    s3_key: str
    workspace_id: UUID
