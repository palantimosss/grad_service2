"""Notification handlers."""

import logging

from aiogram import Router, types

from bot.database.crud_modules.notification_crud import (
    get_notifications_by_user_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session

logger = logging.getLogger(__name__)

notification_router = Router()


def _format_notification_title(notif: object) -> str:
    """Format notification with read/unread mark."""
    read_mark = "✅" if notif.is_read else "🔔"  # type: ignore[union-attr]
    return f"{read_mark} {notif.title}"  # type: ignore[union-attr]


def _build_notifications_text(notifications: list) -> str:
    """Build notifications list text."""
    lines = ["<b>Уведомления</b>", ""]
    lines.extend(
        _format_notification_title(notif) for notif in notifications[:10]
    )
    return "\n".join(lines)


@notification_router.callback_query(lambda c: c.data == "notifications")
async def show_notifications(callback: types.CallbackQuery) -> None:
    """Show user notifications."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(
                "Сначала зарегистрируйтесь", show_alert=True,
            )
            return
        notifications = await get_notifications_by_user_id(session, user.id)
        if not notifications:
            await callback.message.edit_text("Уведомлений нет.")
            return
        text = _build_notifications_text(notifications)
        await callback.message.edit_text(text)
