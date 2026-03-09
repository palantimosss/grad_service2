"""Notification service module."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud_modules.notification_crud import (
    create_notification as create_notification_db,
)
from bot.database.models.enums import NotificationType


class NotificationParams(TypedDict, total=False):
    """Parameters for notification."""

    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    related_entity_type: str | None
    related_entity_id: int | None


async def send_notification(
    session: AsyncSession,
    params: NotificationParams,
) -> object | None:
    """Send notification to user."""
    return await create_notification_db(session=session, params=params)


async def notify_new_project(
    session: AsyncSession,
    manager_id: int,
    project_title: str,
) -> None:
    """Notify manager about new project."""
    await send_notification(
        session=session,
        params={
            "user_id": manager_id,
            "title": "Новая заявка",
            "message": f"Создана новая заявка на проект: {project_title}",
            "notification_type": NotificationType.NEW_PROJECT,
            "related_entity_type": "project",
        },
    )


async def notify_project_registered(
    session: AsyncSession,
    client_id: int,
    project_title: str,
) -> None:
    """Notify client about project registration."""
    await send_notification(
        session=session,
        params={
            "user_id": client_id,
            "title": "Проект зарегистрирован",
            "message": f"Ваш проект '{project_title}' зарегистрирован",
            "notification_type": NotificationType.PROJECT_REGISTERED,
            "related_entity_type": "project",
        },
    )


async def notify_new_task(
    session: AsyncSession,
    performer_id: int,
    task_title: str,
) -> None:
    """Notify performer about new task."""
    await send_notification(
        session=session,
        params={
            "user_id": performer_id,
            "title": "Новая задача",
            "message": f"Вам назначена задача: {task_title}",
            "notification_type": NotificationType.NEW_TASK,
            "related_entity_type": "task",
        },
    )
