"""ClientCompany model."""


from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.database.models.base import Base

# String length constants
NAME_MAX_LENGTH = 255
INN_MAX_LENGTH = 20
KPP_MAX_LENGTH = 20
ADDRESS_MAX_LENGTH = 500
PHONE_MAX_LENGTH = 50
EMAIL_MAX_LENGTH = 255
WEBSITE_MAX_LENGTH = 255


class ClientCompany(Base):
    """Client company model."""

    __tablename__ = "client_companies"

    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH))
    inn: Mapped[str | None] = mapped_column(
        String(INN_MAX_LENGTH), nullable=True,
    )
    kpp: Mapped[str | None] = mapped_column(
        String(KPP_MAX_LENGTH), nullable=True,
    )
    address: Mapped[str | None] = mapped_column(
        String(ADDRESS_MAX_LENGTH), nullable=True,
    )
    phone: Mapped[str | None] = mapped_column(
        String(PHONE_MAX_LENGTH), nullable=True,
    )
    email: Mapped[str | None] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=True,
    )
    website: Mapped[str | None] = mapped_column(
        String(WEBSITE_MAX_LENGTH), nullable=True,
    )

    projects = relationship("Project", back_populates="client_company")
