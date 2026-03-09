"""Feedback model."""


from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base


class Feedback(Base):
    """Feedback model."""

    __tablename__ = "feedbacks"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    message: Mapped[str] = mapped_column(Text)
    rating: Mapped[int | None] = mapped_column(Integer, nullable=True)

    project = relationship("Project", back_populates="feedbacks")
    author = relationship("User", back_populates="feedbacks")
