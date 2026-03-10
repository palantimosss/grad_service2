"""GIS check log model."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base

if TYPE_CHECKING:
    from datetime import datetime

# String length constants
ADDRESS_MAX_LENGTH = 500
COORDINATES_MAX_LENGTH = 100


class GISCheckLog(Base):
    """GIS check log model."""

    __tablename__ = "gis_check_logs"

    meeting_id: Mapped[int] = mapped_column(ForeignKey("meetings.id"))
    address: Mapped[str] = mapped_column(String(ADDRESS_MAX_LENGTH))
    coordinates: Mapped[str | None] = mapped_column(
        String(COORDINATES_MAX_LENGTH),
        nullable=True,
    )
    inside_zone: Mapped[bool]
    checked_at: Mapped[datetime] = mapped_column(DateTime)

    meeting = relationship("Meeting", backref="gis_checks")
