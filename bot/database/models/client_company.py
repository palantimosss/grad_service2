"""ClientCompany model."""


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base


class ClientCompany(Base):
    """Client company model."""

    __tablename__ = "client_companies"

    name: Mapped[str] = mapped_column(String(255))
    inn: Mapped[str | None] = mapped_column(String(20), nullable=True)
    kpp: Mapped[str | None] = mapped_column(String(20), nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    projects = relationship("Project", back_populates="client_company")
