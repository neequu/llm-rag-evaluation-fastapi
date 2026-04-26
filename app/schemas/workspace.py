from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    description: str | None = None


class WorkspaceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)

    description: str | None = None

    is_active: bool | None = None


class WorkspaceResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    description: str | None
    owner_id: UUID
    is_active: bool
