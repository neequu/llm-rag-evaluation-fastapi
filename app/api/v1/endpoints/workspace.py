from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.crud.users import get_current_user
from app.crud.workspace import WorkspaceService
from app.db.db import DBSession
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate

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


@router.get(
    "/{workspace_id}", response_model=WorkspaceRead, status_code=status.HTTP_200_OK
)
async def get_workspace_by_id(
    workspace_id: UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    """
    Returns a workspace by id for the authenticated user.
    """
    return await WorkspaceService.get_workspace_by_id(
        workspace_id=workspace_id,
        db=db,
        owner_id=current_user.id,
    )


@router.get("/", response_model=list[WorkspaceRead], status_code=status.HTTP_200_OK)
async def get_user_workspaces(
    db: DBSession, current_user: User = Depends(get_current_user)
) -> list[Workspace]:
    """
    Returns all workspaces for the authenticated user.
    """
    return await WorkspaceService.get_workspaces(
        db=db,
        owner_id=current_user.id,
    )


@router.patch(
    "/{workspace_id}", response_model=WorkspaceRead, status_code=status.HTTP_200_OK
)
async def update_workspace(
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    """
    Updates a workspace by id for the authenticated user.
    """
    return await WorkspaceService.update_workspace(
        workspace_id=workspace_id,
        db=db,
        schema=payload,
        owner_id=current_user.id,
    )


@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    workspace_id: UUID,
    db: DBSession,
    current_user: User = Depends(get_current_user),
):
    """
    Deletes a workspace by id for the authenticated user.
    """
    return await WorkspaceService.delete_workspace(
        workspace_id=workspace_id, db=db, owner_id=current_user.id
    )
