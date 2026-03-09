"""Project stage model."""

from datetime import datetime

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base

# String length constants
TITLE_MAX_LENGTH = 255
STATUS_MAX_LENGTH = 50


class ProjectStage(Base):
    """Project stage model."""

    __tablename__ = "project_stages"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=0)
    planned_start: Mapped[datetime | None]
    planned_end: Mapped[datetime | None]
    status: Mapped[str] = mapped_column(
        String(STATUS_MAX_LENGTH), default="pending",
    )

    project = relationship("Project", back_populates="stages")
