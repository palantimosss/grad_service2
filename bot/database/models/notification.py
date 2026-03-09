"""Notification model."""

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base

if TYPE_CHECKING:
    from bot.database.models.enums import NotificationType


class Notification(Base):
    """Notification model."""

    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    message: Mapped[str] = mapped_column(Text)
    notification_type: Mapped[NotificationType]
    related_entity_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    related_entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User", back_populates="notifications")
