"""Meeting creation handlers."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.meeting_crud import (
    MeetingCreateParams,
    create_meeting,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.gis.server import check_meeting_address
from bot.states.states import MeetingCreation

logger = logging.getLogger(__name__)

meeting_creation_router = Router()

# Optional meeting fields (immutable tuple)
_OPTIONAL_MEETING_FIELDS = (
    "description",
    "address",
    "coordinates",
    "online_link",
    "gis_check_result",
)

# Skip option text
_SKIP_OPTION = "пропустить"

# Default values
_DEFAULT_DURATION = 60


def _parse_datetime(text: str) -> datetime | None:
    """Parse datetime from text."""
    try:
        return datetime.strptime(text, "%d.%m.%Y %H:%M").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def _add_optional_param(
    meeting_params: dict, meeting_data: dict, field_key: str,
) -> None:
    """Add optional parameter to params if present in data."""
    if meeting_data.get(field_key):
        meeting_params[field_key] = meeting_data[field_key]


def _build_meeting_params(
    meeting_data: dict, user_id: int,
) -> MeetingCreateParams:
    """Build meeting creation params."""
    meeting_params: MeetingCreateParams = {
        "project_id": meeting_data["project_id"],
        "title": meeting_data["title"],
        "organizer_id": user_id,
        "scheduled_at": meeting_data["scheduled_at"],
        "duration_minutes": meeting_data.get("duration", _DEFAULT_DURATION),
        "is_online": meeting_data.get("is_online", False),
    }
    for field_key in _OPTIONAL_MEETING_FIELDS:
        _add_optional_param(meeting_params, meeting_data, field_key)
    return meeting_params


def _format_coordinates(coordinates: tuple) -> str:
    """Format coordinates as string."""
    return f"{coordinates[0]},{coordinates[1]}"


def _get_gis_status(*, is_inside: bool) -> str:
    """Get GIS status string."""
    return "inside" if is_inside else "outside"


async def _create_meeting_in_db(
    message: types.Message,
    meeting_data: dict,
) -> None:
    """Create meeting in database."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        meeting_params = _build_meeting_params(meeting_data, user.id)
        await create_meeting(session=session, params=meeting_params)


async def create_meeting_final(
    message: types.Message, state: FSMContext,
) -> None:
    """Finalize meeting creation."""
    meeting_data = await state.get_data()
    await _create_meeting_in_db(message, meeting_data)
    await message.answer("Встреча создана!")
    await state.clear()


@meeting_creation_router.callback_query(
    lambda c: c.data.startswith("create_meeting_"),
)
async def create_meeting_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start meeting creation."""
    parts = callback.data.split("_")
    project_id = int(parts[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text(
        "Создание встречи.\nВведите название:",
    )
    await state.set_state(MeetingCreation.title)


@meeting_creation_router.message(MeetingCreation.title)
async def meeting_title(message: types.Message, state: FSMContext) -> None:
    """Process meeting title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(MeetingCreation.description)


@meeting_creation_router.message(MeetingCreation.description)
async def meeting_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting description."""
    desc_val: str | None = None
    if message.text != _SKIP_OPTION:
        desc_val = message.text
    await state.update_data(description=desc_val)
    await message.answer("Дата и время (ДД.ММ.ГГГГ ЧЧ:ММ):")
    await state.set_state(MeetingCreation.scheduled_at)


@meeting_creation_router.message(MeetingCreation.scheduled_at)
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


@meeting_creation_router.message(MeetingCreation.duration)
async def meeting_duration(
    message: types.Message, state: FSMContext,
) -> None:
    """Process meeting duration."""
    duration_val = _DEFAULT_DURATION
    if message.text != _SKIP_OPTION:
        try:
            duration_val = int(message.text)
        except ValueError:
            await message.answer("Введите число:")
            return
    await state.update_data(duration=duration_val)
    await message.answer("Формат встречи:\n1. Офлайн\n2. Онлайн")
    await state.set_state(MeetingCreation.format_type)


@meeting_creation_router.message(MeetingCreation.format_type)
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


@meeting_creation_router.message(MeetingCreation.online_link)
async def meeting_online_link(
    message: types.Message, state: FSMContext,
) -> None:
    """Process online link and create meeting."""
    await state.update_data(online_link=message.text)
    await create_meeting_final(message, state)


async def _handle_gis_result(
    message: types.Message,
    state: FSMContext,
    address_val: str,
    gis_result: object,
) -> bool:
    """Handle GIS check result. Returns True if should continue."""
    await state.update_data(
        address=address_val,
        coordinates=_format_coordinates(gis_result.coordinates),
        gis_check_result=_get_gis_status(is_inside=gis_result.inside_zone),
    )
    if not gis_result.inside_zone:
        await message.answer(
            f"⚠️ {gis_result.message}\n"
            "Рекомендуем онлайн-встречу. Продолжить? (да/нет):",
        )
        return False
    return True


@meeting_creation_router.message(MeetingCreation.address)
async def meeting_address(
    message: types.Message, state: FSMContext,
) -> None:
    """Process address, check via GIS, and create meeting."""
    address_val = message.text
    gis_result = await check_meeting_address(address_val)
    if not gis_result.success:
        await message.answer(
            f"Ошибка: {gis_result.message}\n"
            "Попробуйте другой адрес или выберите онлайн:",
        )
        return
    should_continue = await _handle_gis_result(
        message, state, address_val, gis_result,
    )
    if should_continue:
        await create_meeting_final(message, state)
