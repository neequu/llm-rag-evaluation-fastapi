import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.core.queue import get_redis
from app.core.s3 import s3_client
from app.crud.documents import DocumentService
from app.crud.workspace import WorkspaceService
from app.db.db import DBSession
from app.dependencies.auth import CurrentUser
from app.models.workspace import Workspace
from app.schemas.documents import DocumentCreate, DocumentRead
from app.schemas.workspace import WorkspaceCreate, WorkspaceRead, WorkspaceUpdate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["Workspaces"])


@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
async def create_workspace(
    payload: WorkspaceCreate, db: DBSession, current_user: CurrentUser
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
    current_user: CurrentUser,
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
    db: DBSession, current_user: CurrentUser
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
    current_user: CurrentUser,
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
    current_user: CurrentUser,
):
    """
    Deletes a workspace by id for the authenticated user.
    """
    return await WorkspaceService.delete_workspace(
        workspace_id=workspace_id, db=db, owner_id=current_user.id
    )


ALLOWED_CONTENT_TYPES = {
    "text/plain",
    "text/csv",
    "text/markdown",
    "application/octet-stream",
}

MAX_FILE_SIZE = 100 * 1024 * 1024


@router.post(
    "/{workspace_id}/documents/upload",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(
    workspace_id: UUID,
    file: Annotated[UploadFile, File(description="File to upload")],
    current_user: CurrentUser,
    db: DBSession,
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Content type {file.content_type!r} is not allowed. "
            f"Allowed: {sorted(ALLOWED_CONTENT_TYPES)}",
        )

    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    object_key = await s3_client.upload_file(
        file_obj=file.file,
        content_type=file.content_type or "application/octet-stream",
        extra_metadata={
            "original_filename": file.filename or "unknown",
            "user_id": str(current_user.id),
        },
    )

    document = await DocumentService.create_document(
        db=db,
        uploader_id=current_user.id,
        data=DocumentCreate(
            filename=file.filename or "unknown",
            content_type=file.content_type or "application/octet-stream",
            file_size=file_size,
            s3_key=object_key,
            workspace_id=workspace_id,
        ),
    )

    redis = await get_redis()

    await redis.enqueue_job(
        "ingest_document",
        document.id,
        workspace_id,
        current_user.id,
    )

    return document


@router.get(
    "/{workspace_id}/documents",
    response_model=list[DocumentRead],
    status_code=status.HTTP_200_OK,
)
async def get_workspace_documents(
    workspace_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    documents = await DocumentService.get_documents(
        db=db,
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

    return documents


@router.get(
    "/{workspace_id}/documents/{document_id}",
    response_model=DocumentRead,
    status_code=status.HTTP_200_OK,
)
async def get_workspace_document(
    workspace_id: UUID,
    document_id: UUID,
    current_user: CurrentUser,
    db: DBSession,
):
    document = await DocumentService.get_document(
        db=db,
        document_id=document_id,
        workspace_id=workspace_id,
        owner_id=current_user.id,
    )

    return document
