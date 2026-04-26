from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.db.mixins import TimestampMixin, UUIDMixin


class Workspace(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255))

    description: Mapped[str] = mapped_column(String(500))

    owner_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    is_active: Mapped[bool] = mapped_column(default=True)

    owner: Mapped["User"] = relationship(back_populates="workspaces")
