"""Task model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base
from bot.database.models.enums import TaskStatus

if TYPE_CHECKING:
    from datetime import datetime

# String length constants
TITLE_MAX_LENGTH = 255


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.PENDING)
    performer_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    deadline: Mapped[datetime | None]
    priority: Mapped[int] = mapped_column(Integer, default=3)

    project = relationship("Project", back_populates="tasks")
    performer = relationship(
        "User",
        foreign_keys=[performer_id],
        back_populates="tasks_as_performer",
    )
    manager = relationship(
        "User",
        foreign_keys=[manager_id],
        back_populates="tasks_as_manager",
    )
    documents = relationship(
        "Document",
        back_populates="task",
        cascade="all, delete-orphan",
    )
