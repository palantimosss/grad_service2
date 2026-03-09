"""Common keyboards: back, yes/no, cancel."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

# Button text constants
_BACK_TEXT = "Назад"
_CANCEL_TEXT = "Отмена"
_YES_TEXT = "Да"
_NO_TEXT = "Нет"

# Callback data constants
_BACK_MENU = "back_to_menu"
_BACK_PROFILE = "back_to_profile"
_BACK_PROJECT = "back_to_project"
_BACK_TASKS = "back_to_tasks"
_BACK_MEETINGS = "back_to_meetings"
_BACK_DOCUMENTS = "back_to_documents"
_BACK_NOTIFICATIONS = "back_to_notifications"


def _adjust_single(builder: InlineKeyboardBuilder) -> None:
    """Adjust builder to single column."""
    builder.adjust(1)


def _adjust_double(builder: InlineKeyboardBuilder) -> None:
    """Adjust builder to double column."""
    builder.adjust(2)


def _build_single_column_keyboard(
    buttons: list[tuple[str, str]],
) -> InlineKeyboardMarkup:
    """Build single column keyboard from button list."""
    builder = InlineKeyboardBuilder()
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    _adjust_single(builder)
    return builder.as_markup()


def _build_double_column_keyboard(
    buttons: list[tuple[str, str]],
) -> InlineKeyboardMarkup:
    """Build double column keyboard from button list."""
    builder = InlineKeyboardBuilder()
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    _adjust_double(builder)
    return builder.as_markup()


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Get yes/no keyboard."""
    return _build_double_column_keyboard([
        (_YES_TEXT, "yes"),
        (_NO_TEXT, "no"),
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    return _build_single_column_keyboard([
        (_CANCEL_TEXT, "cancel"),
    ])


def get_back_keyboard(
    callback: str = _BACK_MENU,
) -> InlineKeyboardMarkup:
    """Get simple back keyboard."""
    return _build_single_column_keyboard([
        (_BACK_TEXT, callback),
    ])
