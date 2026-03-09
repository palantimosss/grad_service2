"""GIS check log model."""

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from datetime import datetime

from bot.database.models.base import Base


class GISCheckLog(Base):
    """GIS check log model."""

    __tablename__ = "gis_check_logs"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    address: Mapped[str] = mapped_column(String(500))
    coordinates: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    inside_zone: Mapped[bool]
    checked_at: Mapped[datetime] = mapped_column(DateTime)

    meeting = relationship("Meeting", backref="gis_checks")
