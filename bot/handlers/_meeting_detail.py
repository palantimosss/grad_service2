"""Meeting detail and response handlers."""

import logging

from aiogram import Router, types

from bot.database.crud_modules.meeting_crud import (
    get_meeting_by_id,
    update_meeting_status,
)
from bot.database.database import get_session
from bot.database.models.enums import MeetingStatus
from bot.keyboards.menus import (
    get_meeting_response_keyboard,
)

logger = logging.getLogger(__name__)

meeting_detail_router = Router()

# Status map for display (immutable tuple)
_STATUS_MAP = (
    ("pending", "Ожидает"),
    ("confirmed", "Подтверждена"),
    ("cancelled", "Отменена"),
    ("completed", "Завершена"),
)


def _get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, label in _STATUS_MAP:
        if key == status_value:
            return label
    return status_value


def _build_meeting_text(meeting: object) -> str:
    """Build meeting detail text."""
    format_label = "Онлайн" if meeting.is_online else "Офлайн"
    location = meeting.online_link if meeting.is_online else meeting.address
    loc_text = location or "Не указана"
    status_text = _get_status_text(meeting.status.value)
    return "\n".join([
        f"<b>{meeting.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Формат: {format_label}",
        f"Локация: {loc_text}",
        f"Дата: {meeting.scheduled_at}",
        f"Длительность: {meeting.duration_minutes} мин",
    ])


def _get_callback_data(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def _get_meeting_id_from_callback(callback: types.CallbackQuery) -> int:
    """Extract meeting ID from callback data."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[1])


def _get_meeting_id_from_action_callback(callback: types.CallbackQuery) -> int:
    """Extract meeting ID from action callback data."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[2])


async def _update_meeting_status_in_db(
    meeting_id: int,
    status: MeetingStatus,
) -> None:
    """Update meeting status in database."""
    async for session in get_session():
        await update_meeting_status(session, meeting_id, status)


async def _show_meeting_info(callback: types.CallbackQuery) -> None:
    """Show meeting information."""
    meeting_id = _get_meeting_id_from_callback(callback)
    async for session in get_session():
        meeting = await get_meeting_by_id(session, meeting_id)
        if not meeting:
            await callback.answer("Встреча не найдена", show_alert=True)
            return
        text = _build_meeting_text(meeting)
        if meeting.status == MeetingStatus.PENDING:
            await callback.message.edit_text(
                text,
                reply_markup=get_meeting_response_keyboard(meeting_id),
            )
        else:
            await callback.message.edit_text(text)


@meeting_detail_router.callback_query(
    lambda c: c.data.startswith("meeting_"),
)
async def meeting_detail(callback: types.CallbackQuery) -> None:
    """Show meeting details."""
    callback_data = _get_callback_data(callback)
    if callback_data.startswith("meeting_confirm_"):
        await _update_meeting_status_in_db(
            _get_meeting_id_from_action_callback(callback),
            MeetingStatus.CONFIRMED,
        )
        await callback.message.edit_text("Встреча подтверждена!")
        return
    if callback_data.startswith("meeting_decline_"):
        await _update_meeting_status_in_db(
            _get_meeting_id_from_action_callback(callback),
            MeetingStatus.CANCELLED,
        )
        await callback.message.edit_text("Встреча отклонена.")
        return
    await _show_meeting_info(callback)
