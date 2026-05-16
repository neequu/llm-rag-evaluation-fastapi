from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import UUIDMixin


class DocumentChunk(Base, UUIDMixin):
    __tablename__ = "document_chunks"

    document_id: Mapped[UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    chunk_index: Mapped[int]
    content: Mapped[str]
    token_count: Mapped[int | None]
    chroma_id: Mapped[str | None] = mapped_column(String(255), unique=True)

    document: Mapped["Document"] = relationship(back_populates="chunks")
