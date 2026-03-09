"""Notification CRUD operations."""

from bot.database.crud_modules.notification_crud import (
    NotificationCreateParams,
    create_notification,
    delete_notification,
    get_notification_by_id,
    get_notifications_by_user_id,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)

__all__ = [
    "NotificationCreateParams",
    "create_notification",
    "delete_notification",
    "get_notification_by_id",
    "get_notifications_by_user_id",
    "mark_all_notifications_as_read",
    "mark_notification_as_read",
]
