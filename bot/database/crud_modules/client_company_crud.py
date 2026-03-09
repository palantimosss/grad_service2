"""ClientCompany CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.client_company import ClientCompany


class CompanyCreateParams(TypedDict, total=False):
    """Parameters for creating a company."""

    name: str
    inn: str | None
    kpp: str | None
    address: str | None
    phone: str | None
    email: str | None
    website: str | None


async def get_company_by_id(
    session: AsyncSession, company_id: int,
) -> ClientCompany | None:
    """Get company by ID."""
    result = await session.execute(
        select(ClientCompany).where(ClientCompany.id == company_id),
    )
    return result.scalar_one_or_none()


async def get_all_companies(
    session: AsyncSession,
) -> list[ClientCompany]:
    """Get all companies."""
    result = await session.execute(select(ClientCompany))
    return list(result.scalars().all())


async def create_company(
    session: AsyncSession, params: CompanyCreateParams,
) -> ClientCompany:
    """Create a new company."""
    company = ClientCompany(**params)
    session.add(company)
    await session.commit()
    await session.refresh(company)
    return company


async def update_company(
    session: AsyncSession,
    company_id: int,
    params: CompanyCreateParams,
) -> ClientCompany | None:
    """Update company fields."""
    await session.execute(
        update(ClientCompany)
        .where(ClientCompany.id == company_id)
        .values(**params),
    )
    await session.commit()
    return await get_company_by_id(session, company_id)


async def delete_company(
    session: AsyncSession, company_id: int,
) -> bool:
    """Delete company by ID."""
    result = await session.execute(
        delete(ClientCompany).where(ClientCompany.id == company_id),
    )
    await session.commit()
    return result.rowcount > 0
