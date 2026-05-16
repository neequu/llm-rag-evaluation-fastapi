from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.db import DBSession
from app.models.document import Document
from app.models.workspace import Workspace
from app.schemas.documents import DocumentCreate


async def check_workspace_ownership(
    *, db: DBSession, workspace_id: UUID, owner_id: UUID
):
    workspace_query = select(Workspace).where(
        Workspace.id == workspace_id, Workspace.owner_id == owner_id
    )
    workspace_result = await db.execute(workspace_query)

    workspace = workspace_result.scalar_one_or_none()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace not found or unauthorized",
        )

    return workspace


class DocumentService:
    @staticmethod
    async def create_document(
        *,
        db: DBSession,
        data: DocumentCreate,
        uploader_id: UUID,
    ) -> Document:
        document = Document(
            **data.model_dump(),
            uploader_id=uploader_id,
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        return document

    @staticmethod
    async def get_documents(
        *,
        db: DBSession,
        owner_id: UUID,
        workspace_id: UUID,
    ) -> list[Document]:

        await check_workspace_ownership(
            db=db, owner_id=owner_id, workspace_id=workspace_id
        )

        query = select(Document).where(
            Document.workspace_id == workspace_id,
        )
        result = await db.execute(query)

        documents = result.scalars().all()

        return list(documents)

    @staticmethod
    async def get_document(
        *,
        db: DBSession,
        owner_id: UUID,
        workspace_id: UUID,
        document_id: UUID,
    ) -> Document:

        await check_workspace_ownership(
            db=db, owner_id=owner_id, workspace_id=workspace_id
        )

        query = select(Document).where(
            Document.id == document_id,
            Document.workspace_id == workspace_id,
        )
        result = await db.execute(query)

        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found or unauthorized",
            )

        return document
