from uuid import UUID

from pgvector import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.db.mixins import UUIDMixin


class DocumentChunk(Base, UUIDMixin):
    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id"),
        index=True,
    )

    chunk_index: Mapped[int]

    content: Mapped[str]

    embedding: Mapped[Vector] = mapped_column(Vector(384))
