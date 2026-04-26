from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.crud.users import get_current_user
from app.crud.workspace import WorkspaceService
from app.db.db import DBSession
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    """
    Creates a new workspace for the authenticated user.
    """
    return await WorkspaceService.create_workspace(
        db=db, schema=payload, owner_id=current_user.id
    )


async def get_workspace_by_id(): ...


async def get_user_workspaces(db: DBSession, user_id: UUID) -> list[Workspace]: ...


async def update_workspace(): ...


async def delete_workspace(): ...
