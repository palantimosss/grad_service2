"""Meeting and MeetingParticipant models."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from datetime import datetime

from bot.database.models.base import Base
from bot.database.models.enums import MeetingParticipantStatus, MeetingStatus


class Meeting(Base):
    """Meeting model."""

    __tablename__ = "meetings"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    organizer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    scheduled_at: Mapped[datetime]
    duration_minutes: Mapped[int] = mapped_column(Integer, default=60)
    status: Mapped[MeetingStatus] = mapped_column(
        default=MeetingStatus.PENDING,
    )
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    coordinates: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    is_online: Mapped[bool] = mapped_column(Boolean, default=False)
    online_link: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    gis_check_result: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    project = relationship("Project", back_populates="meetings")
    organizer = relationship("User", back_populates="organized_meetings")
    participants = relationship(
        "MeetingParticipant",
        back_populates="meeting",
        cascade="all, delete-orphan",
    )


class MeetingParticipant(Base):
    """Meeting participant model."""

    __tablename__ = "meeting_participants"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    status: Mapped[MeetingParticipantStatus] = mapped_column(
        default=MeetingParticipantStatus.PENDING,
    )

    meeting = relationship("Meeting", back_populates="participants")
    user = relationship("User", back_populates="meeting_participations")
