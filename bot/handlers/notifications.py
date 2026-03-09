"""Notifications and meetings handlers."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import F, Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.meeting_crud import (
    MeetingCreateParams,
    create_meeting,
    get_meeting_by_id,
    update_meeting_status,
)
from bot.database.crud_modules.notification_crud import (
    get_notifications_by_user_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import MeetingStatus
from bot.gis.server import check_meeting_address
from bot.keyboards.menus import (
    get_meeting_response_keyboard,
)
from bot.states.states import MeetingCreation

logger = logging.getLogger(__name__)

notifications_router = Router()

STATUS_MAP = {
    "pending": "Ожидает",
    "confirmed": "Подтверждена",
    "cancelled": "Отменена",
    "completed": "Завершена",
}


def _parse_datetime(text: str) -> datetime | None:
    """Parse datetime from text."""
    try:
        return datetime.strptime(text, "%d.%m.%Y %H:%M").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def _add_optional_param(
    params: dict, data: dict, key: str,
) -> None:
    """Add optional parameter to params if present in data."""
    if data.get(key):
        params[key] = data[key]


def _build_meeting_params(
    data: dict, user_id: int,
) -> MeetingCreateParams:
    """Build meeting creation params."""
    params: MeetingCreateParams = {
        "project_id": data["project_id"],
        "title": data["title"],
        "organizer_id": user_id,
        "scheduled_at": data["scheduled_at"],
        "duration_minutes": data.get("duration", 60),
        "is_online": data.get("is_online", False),
    }
    for key in [
        "description",
        "address",
        "coordinates",
        "online_link",
        "gis_check_result",
    ]:
        _add_optional_param(params, data, key)
    return params


def _build_meeting_text(meeting: object) -> str:
    """Build meeting detail text."""
    format_str = "Онлайн" if meeting.is_online else "Офлайн"
    location = meeting.online_link if meeting.is_online else meeting.address
    loc_text = location or "Не указана"
    status_text = STATUS_MAP.get(meeting.status.value, meeting.status.value)
    lines = [
        f"<b>{meeting.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Формат: {format_str}",
        f"Локация: {loc_text}",
        f"Дата: {meeting.scheduled_at}",
        f"Длительность: {meeting.duration_minutes} мин",
    ]
    return "\n".join(lines)


@notifications_router.callback_query(F.data.startswith("create_meeting_"))
async def create_meeting_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start meeting creation."""
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text(
        "Создание встречи.\nВведите название:",
    )
    await state.set_state(MeetingCreation.title)


@notifications_router.message(MeetingCreation.title)
async def meeting_title(message: types.Message, state: FSMContext) -> None:
    """Process meeting title."""
    await state.update_data(title=message.text)
    await message.answer("Введите описание (или 'пропустить'):")
    await state.set_state(MeetingCreation.description)


@notifications_router.message(MeetingCreation.description)
async def meeting_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting description."""
    desc: str | None = None
    if message.text != "пропустить":
        desc = message.text
    await state.update_data(description=desc)
    await message.answer("Дата и время (ДД.ММ.ГГГГ ЧЧ:ММ):")
    await state.set_state(MeetingCreation.scheduled_at)


@notifications_router.message(MeetingCreation.scheduled_at)
async def meeting_scheduled_at(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting scheduled time."""
    scheduled_at = _parse_datetime(message.text)
    if scheduled_at is None:
        await message.answer("Неверный формат:")
        return
    await state.update_data(scheduled_at=scheduled_at)
    await message.answer("Длительность в минутах (или 'пропустить'):")
    await state.set_state(MeetingCreation.duration)


@notifications_router.message(MeetingCreation.duration)
async def meeting_duration(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting duration."""
    duration = 60
    if message.text != "пропустить":
        try:
            duration = int(message.text)
        except ValueError:
            await message.answer("Введите число:")
            return
    await state.update_data(duration=duration)
    await message.answer("Формат встречи:\n1. Офлайн\n2. Онлайн")
    await state.set_state(MeetingCreation.format_type)


@notifications_router.message(MeetingCreation.format_type)
async def meeting_format(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting format."""
    is_online = message.text == "2"
    await state.update_data(is_online=is_online)
    if is_online:
        await message.answer("Введите ссылку на встречу:")
        await state.set_state(MeetingCreation.online_link)
    else:
        await message.answer("Введите адрес встречи:")
        await state.set_state(MeetingCreation.address)


@notifications_router.message(MeetingCreation.online_link)
async def meeting_online_link(
    message: types.Message, state: FSMContext,
) -> None:
    """Process online link and create meeting."""
    await state.update_data(online_link=message.text)
    await create_meeting_final(message, state)


@notifications_router.message(MeetingCreation.address)
async def meeting_address(
    message: types.Message, state: FSMContext,
) -> None:
    """Process address, check via GIS, and create meeting."""
    address = message.text
    gis_result = await check_meeting_address(address)
    if not gis_result.success:
        await message.answer(
            f"Ошибка: {gis_result.message}\n"
            "Попробуйте другой адрес или выберите онлайн:",
        )
        return
    coords = f"{gis_result.coordinates[0]},{gis_result.coordinates[1]}"
    gis_status = "inside" if gis_result.inside_zone else "outside"
    await state.update_data(
        address=address,
        coordinates=coords,
        gis_check_result=gis_status,
    )
    if not gis_result.inside_zone:
        await message.answer(
            f"⚠️ {gis_result.message}\n"
            "Рекомендуем онлайн-встречу. Продолжить? (да/нет):",
        )
        return
    await create_meeting_final(message, state)


async def create_meeting_final(
    message: types.Message, state: FSMContext,
) -> None:
    """Finalize meeting creation."""
    data = await state.get_data()
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        params = _build_meeting_params(data, user.id)
        await create_meeting(session=session, params=params)
    await message.answer("Встреча создана!")
    await state.clear()


@notifications_router.callback_query(F.data.startswith("meeting_"))
async def meeting_detail(callback: types.CallbackQuery) -> None:
    """Show meeting details."""
    data = callback.data
    if data.startswith("meeting_confirm_"):
        await _confirm_meeting(callback)
        return
    if data.startswith("meeting_decline_"):
        await _decline_meeting(callback)
        return
    await _show_meeting_info(callback)


async def _confirm_meeting(callback: types.CallbackQuery) -> None:
    """Confirm meeting."""
    meeting_id = int(callback.data.split("_")[2])
    async for session in get_session():
        await update_meeting_status(
            session, meeting_id, MeetingStatus.CONFIRMED,
        )
    await callback.message.edit_text("Встреча подтверждена!")


async def _decline_meeting(callback: types.CallbackQuery) -> None:
    """Decline meeting."""
    meeting_id = int(callback.data.split("_")[2])
    async for session in get_session():
        await update_meeting_status(
            session, meeting_id, MeetingStatus.CANCELLED,
        )
    await callback.message.edit_text("Встреча отклонена.")


async def _show_meeting_info(callback: types.CallbackQuery) -> None:
    """Show meeting information."""
    meeting_id = int(callback.data.split("_")[1])
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


@notifications_router.callback_query(F.data == "notifications")
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
        lines = ["<b>Уведомления</b>", ""]
        for notif in notifications[:10]:
            read_mark = "✅" if notif.is_read else "🔔"
            lines.append(f"{read_mark} {notif.title}")
        text = "\n".join(lines)
        await callback.message.edit_text(text)
