"""Project model."""

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base
from bot.database.models.enums import ProjectStatus

if TYPE_CHECKING:
    from datetime import datetime

# String length constants
TITLE_MAX_LENGTH = 255

# Relationship cascade constants
CASCADE_DELETE = "all, delete-orphan"


class Project(Base):
    """Project model."""

    __tablename__ = "projects"

    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        default=ProjectStatus.DRAFT,
    )
    client_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    manager_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id"),
        nullable=True,
    )
    client_company_id: Mapped[int | None] = mapped_column(
        ForeignKey("client_companies.id"),
        nullable=True,
    )
    deadline: Mapped[datetime | None]
    budget: Mapped[float | None] = mapped_column(Float, nullable=True)

    client = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="projects_as_client",
    )
    manager = relationship(
        "User",
        foreign_keys=[manager_id],
        back_populates="projects_as_manager",
    )
    client_company = relationship("ClientCompany", back_populates="projects")
    tasks = relationship(
        "Task",
        back_populates="project",
        cascade=CASCADE_DELETE,
    )
    stages = relationship(
        "ProjectStage",
        back_populates="project",
        cascade=CASCADE_DELETE,
    )
    documents = relationship(
        "Document",
        back_populates="project",
        cascade=CASCADE_DELETE,
    )
    meetings = relationship(
        "Meeting",
        back_populates="project",
        cascade=CASCADE_DELETE,
    )
    feedbacks = relationship(
        "Feedback",
        back_populates="project",
        cascade=CASCADE_DELETE,
    )
