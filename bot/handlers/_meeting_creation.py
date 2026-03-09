"""Meeting creation handlers."""

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.gis.server import check_meeting_address
from bot.handlers._meeting_helpers import (
    create_meeting_in_db,
    get_default_duration,
    get_skip_option,
    handle_gis_result,
    parse_datetime,
)
from bot.states.states import MeetingCreation

logger = logging.getLogger(__name__)

meeting_creation_router = Router()

_SKIP_OPTION = get_skip_option()
_DEFAULT_DURATION = get_default_duration()


async def create_meeting_final(
    message: types.Message, state: FSMContext,
) -> None:
    """Finalize meeting creation."""
    meeting_data = await state.get_data()
    await create_meeting_in_db(message, meeting_data)
    await message.answer("Встреча создана!")
    await state.clear()


@meeting_creation_router.callback_query(
    lambda callback: callback.data.startswith("create_meeting_"),
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
async def meeting_title(
    message: types.Message, state: FSMContext,
) -> None:
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
    scheduled_at = parse_datetime(message.text)
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
    should_continue = await handle_gis_result(
        message, state, address_val, gis_result,
    )
    if should_continue:
        await create_meeting_final(message, state)
