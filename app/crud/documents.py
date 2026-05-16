from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select

from app.db.db import DBSession
from app.models.document import Document
from app.schemas.documents import DocumentCreate


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
