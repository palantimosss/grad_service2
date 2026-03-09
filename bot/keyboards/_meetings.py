"""Meeting keyboards: meetings list, meeting response."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.enums import MeetingStatus

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_MEETINGS,
    _BACK_MENU,
    _BACK_TEXT,
    _adjust_single,
    _build_double_column_keyboard,
)


def _get_meeting_emoji(status: MeetingStatus) -> str:
    """Get emoji for meeting status."""
    status_emoji = {
        MeetingStatus.PENDING: "⏳",
        MeetingStatus.CONFIRMED: "✅",
        MeetingStatus.CANCELLED: "❌",
        MeetingStatus.COMPLETED: "✔️",
    }
    return status_emoji.get(status, "📅")


def get_meetings_keyboard(meetings: list) -> InlineKeyboardMarkup:
    """Get meetings list keyboard."""
    builder = InlineKeyboardBuilder()
    for meeting in meetings:
        emoji = _get_meeting_emoji(meeting.status)
        builder.button(
            text=f"{emoji} {meeting.title}",
            callback_data=f"meeting_{meeting.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def get_meeting_response_keyboard(
    meeting_id: int,
) -> InlineKeyboardMarkup:
    """Get meeting response keyboard."""
    return _build_double_column_keyboard([
        ("Подтвердить", f"meeting_confirm_{meeting_id}"),
        ("Отклонить", f"meeting_decline_{meeting_id}"),
        (_BACK_TEXT, _BACK_MEETINGS),
    ])
