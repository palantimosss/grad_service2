"""Document model."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base
from bot.database.models.enums import DocumentType


class Document(Base):
    """Document model."""

    __tablename__ = "documents"

    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"))
    task_id: Mapped[int | None] = mapped_column(
        ForeignKey("tasks.id"), nullable=True,
    )
    file_path: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(255))
    file_size: Mapped[int] = mapped_column(Integer)
    document_type: Mapped[DocumentType] = mapped_column(
        default=DocumentType.OTHER,
    )
    uploaded_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project = relationship("Project", back_populates="documents")
    task = relationship("Task", back_populates="documents")
    uploader = relationship("User", back_populates="uploaded_documents")
