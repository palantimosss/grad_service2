"""Notification CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.enums import NotificationType

from bot.database.models.notification import Notification


class NotificationCreateParams(TypedDict, total=False):
    """Parameters for creating a notification."""

    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    related_entity_type: str | None
    related_entity_id: int | None


async def get_notification_by_id(
    session: AsyncSession, notification_id: int,
) -> Notification | None:
    """Get notification by ID."""
    query_result = await session.execute(
        select(Notification).where(Notification.id == notification_id),
    )
    return query_result.scalar_one_or_none()


async def get_notifications_by_user_id(
    session: AsyncSession, user_id: int,
) -> list[Notification]:
    """Get notifications by user ID."""
    query_result = await session.execute(
        select(Notification)
        .where(Notification.user_id == user_id)
        .order_by(Notification.created_at.desc()),
    )
    return list(query_result.scalars().all())


async def get_unread_notifications(
    session: AsyncSession, user_id: int,
) -> list[Notification]:
    """Get unread notifications for user."""
    query_result = await session.execute(
        select(Notification).where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        ),
    )
    return list(query_result.scalars().all())


async def create_notification(
    session: AsyncSession, notification_data: NotificationCreateParams,
) -> Notification:
    """Create a new notification."""
    notification = Notification(**notification_data)
    session.add(notification)
    await session.commit()
    await session.refresh(notification)
    return notification


async def mark_notification_as_read(
    session: AsyncSession, notification_id: int,
) -> Notification | None:
    """Mark notification as read."""
    await session.execute(
        update(Notification)
        .where(Notification.id == notification_id)
        .values(is_read=True),
    )
    await session.commit()
    return await get_notification_by_id(session, notification_id)


async def mark_all_notifications_as_read(
    session: AsyncSession, user_id: int,
) -> int:
    """Mark all notifications as read for user."""
    query_result = await session.execute(
        update(Notification)
        .where(
            Notification.user_id == user_id,
            Notification.is_read.is_(False),
        )
        .values(is_read=True),
    )
    await session.commit()
    return query_result.rowcount


async def delete_notification(
    session: AsyncSession, notification_id: int,
) -> bool:
    """Delete notification by ID."""
    query_result = await session.execute(
        delete(Notification).where(Notification.id == notification_id),
    )
    await session.commit()
    return query_result.rowcount > 0
