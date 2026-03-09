"""User model."""

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base
from bot.database.models.enums import UserRole


class User(Base):
    """User model representing system users."""

    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(String(255))
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(default=UserRole.CLIENT)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    projects_as_client = relationship(
        "Project",
        foreign_keys="Project.client_id",
        back_populates="client",
    )
    projects_as_manager = relationship(
        "Project",
        foreign_keys="Project.manager_id",
        back_populates="manager",
    )
    tasks_as_performer = relationship(
        "Task",
        foreign_keys="Task.performer_id",
        back_populates="performer",
    )
    tasks_as_manager = relationship(
        "Task",
        foreign_keys="Task.manager_id",
        back_populates="manager",
    )
    organized_meetings = relationship(
        "Meeting",
        foreign_keys="Meeting.organizer_id",
        back_populates="organizer",
    )
    meeting_participations = relationship(
        "MeetingParticipant", back_populates="user",
    )
    uploaded_documents = relationship("Document", back_populates="uploader")
    notifications = relationship("Notification", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="author")
