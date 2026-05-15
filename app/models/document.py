import enum
from uuid import UUID

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class DocumentState(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Document(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "documents"

    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(50))

    s3_key: Mapped[str] = mapped_column(String(512), unique=True, index=True)

    file_size: Mapped[int] = mapped_column(BigInteger)

    status: Mapped[DocumentState] = mapped_column(default=DocumentState.PENDING)

    is_active: Mapped[bool] = mapped_column(default=True)

    workspace_id: Mapped[UUID] = mapped_column(ForeignKey("workspaces.id"), index=True)
    uploader_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"), index=True)

    workspace: Mapped["Workspace"] = relationship(back_populates="documents")
    uploader: Mapped["User"] = relationship(back_populates="documents")
