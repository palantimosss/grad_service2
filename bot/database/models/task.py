"""Task model."""

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from datetime import datetime

from bot.database.models.base import Base
from bot.database.models.enums import TaskStatus


class Task(Base):
    """Task model."""

    __tablename__ = "tasks"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
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
