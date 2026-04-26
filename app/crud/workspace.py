from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.db import DBSession
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate


class WorkspaceService:
    @staticmethod
    async def create_workspace(
        *, db: DBSession, schema: WorkspaceCreate, owner_id: UUID
    ) -> Workspace:
        new_workspace = Workspace(**schema.model_dump(), owner_id=owner_id)

        db.add(new_workspace)
        await db.commit()
        await db.refresh(new_workspace)
        return new_workspace

    @staticmethod
    async def update_workspace(
        *, workspace_id: UUID, db: DBSession, schema: WorkspaceUpdate, owner_id: UUID
    ) -> Workspace:

        query = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.owner_id == owner_id
        )
        result = await db.execute(query)

        workspace = result.scalar_one_or_none()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or unauthorized",
            )

        update_data = schema.model_dump(exclude_unset=True)

        for key, value in update_data.items():
            setattr(workspace, key, value)

        await db.commit()
        await db.refresh(workspace)
        return workspace

    @staticmethod
    async def delete_workspace(
        *, workspace_id: UUID, db: DBSession, owner_id: UUID
    ) -> None:

        query = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.owner_id == owner_id
        )
        result = await db.execute(query)

        workspace = result.scalar_one_or_none()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or unauthorized",
            )
        await db.delete(workspace)
        await db.commit()
        return None

    @staticmethod
    async def get_workspace_by_id(
        *, workspace_id: UUID, db: DBSession, owner_id: UUID
    ) -> Workspace:

        query = select(Workspace).where(
            Workspace.id == workspace_id, Workspace.owner_id == owner_id
        )
        result = await db.execute(query)

        workspace = result.scalar_one_or_none()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found or unauthorized",
            )

        return workspace

    @staticmethod
    async def get_workspaces(*, db: DBSession, owner_id: UUID) -> list[Workspace]:

        query = select(Workspace).where(Workspace.owner_id == owner_id)
        result = await db.execute(query)

        workspaces = result.scalars().all()

        return list(workspaces)
