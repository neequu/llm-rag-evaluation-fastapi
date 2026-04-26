from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select

from app.db.db import DBSession
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate


class WorkspaceService:
    @staticmethod
    async def create_workspace(
        db: DBSession, schema: WorkspaceCreate, owner_id: UUID
    ) -> Workspace:
        new_workspace = Workspace(**schema.model_dump(), owner_id=owner_id)

        db.add(new_workspace)
        await db.commit()
        await db.refresh(new_workspace)
        return new_workspace
