"""User CRUD operations."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.enums import UserRole

from bot.database.models.user import User


class UserCreateParams(TypedDict, total=False):
    """Parameters for creating a user."""

    telegram_id: int
    username: str | None
    first_name: str
    last_name: str | None
    role: UserRole


class UserUpdateParams(TypedDict, total=False):
    """Parameters for updating a user."""

    phone: str | None
    email: str | None
    position: str | None
    role: UserRole
    is_active: bool


async def get_user_by_telegram_id(
    session: AsyncSession, telegram_id: int,
) -> User | None:
    """Get user by Telegram ID."""
    query_result = await session.execute(
        select(User).where(User.telegram_id == telegram_id),
    )
    return query_result.scalar_one_or_none()


async def get_user_by_id(
    session: AsyncSession, user_id: int,
) -> User | None:
    """Get user by internal ID."""
    query_result = await session.execute(
        select(User).where(User.id == user_id),
    )
    return query_result.scalar_one_or_none()


async def create_user(
    session: AsyncSession, user_data: UserCreateParams,
) -> User:
    """Create a new user."""
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def update_user_role(
    session: AsyncSession,
    telegram_id: int,
    role: UserRole,
) -> User | None:
    """Update user role."""
    await session.execute(
        update(User).where(User.telegram_id == telegram_id).values(role=role),
    )
    await session.commit()
    return await get_user_by_telegram_id(session, telegram_id)


async def update_user_profile(
    session: AsyncSession,
    telegram_id: int,
    user_data: UserUpdateParams,
) -> User | None:
    """Update user profile fields."""
    await session.execute(
        update(User)
        .where(User.telegram_id == telegram_id)
        .values(**user_data),
    )
    await session.commit()
    return await get_user_by_telegram_id(session, telegram_id)


async def delete_user(
    session: AsyncSession, telegram_id: int,
) -> bool:
    """Delete user by Telegram ID."""
    query_result = await session.execute(
        delete(User).where(User.telegram_id == telegram_id),
    )
    await session.commit()
    return query_result.rowcount > 0


async def get_all_users(session: AsyncSession) -> list[User]:
    """Get all users."""
    query_result = await session.execute(select(User))
    return list(query_result.scalars().all())


async def get_users_by_role(
    session: AsyncSession, role: UserRole,
) -> list[User]:
    """Get users by role."""
    query_result = await session.execute(
        select(User).where(User.role == role),
    )
    return list(query_result.scalars().all())
