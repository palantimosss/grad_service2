"""Client and notification keyboards."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_MENU,
    _BACK_NOTIFICATIONS,
    _BACK_TEXT,
    _adjust_single,
    _build_single_column_keyboard,
)


def get_clients_keyboard(companies: list) -> InlineKeyboardMarkup:
    """Get clients list keyboard."""
    builder = InlineKeyboardBuilder()
    for company in companies:
        builder.button(
            text=f"🏢 {company.name}",
            callback_data=f"client_{company.id}",
        )
    builder.button(text="Добавить клиента", callback_data="add_client")
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def get_notification_keyboard(
    notification_id: int,
) -> InlineKeyboardMarkup:
    """Get notification keyboard."""
    return _build_single_column_keyboard([
        ("Отметить прочитанным", f"notif_read_{notification_id}"),
        (_BACK_TEXT, _BACK_NOTIFICATIONS),
    ])
