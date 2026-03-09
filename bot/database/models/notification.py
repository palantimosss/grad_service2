"""Notification model."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base

if TYPE_CHECKING:
    from bot.database.models.enums import NotificationType

# String length constants
TITLE_MAX_LENGTH = 255
ENTITY_TYPE_MAX_LENGTH = 50


class Notification(Base):
    """Notification model."""

    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(TITLE_MAX_LENGTH))
    message: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[NotificationType]
    related_entity_type: Mapped[str | None] = mapped_column(
        String(ENTITY_TYPE_MAX_LENGTH),
        nullable=True,
    )
    related_entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
