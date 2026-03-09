"""Project stage model."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from datetime import datetime

from bot.database.models.base import Base


class ProjectStage(Base):
    """Project stage model."""

    __tablename__ = "project_stages"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    planned_start: Mapped[datetime | None]
    planned_end: Mapped[datetime | None]
    status: Mapped[str] = mapped_column(String(50), default="pending")

    project = relationship("Project", back_populates="stages")
