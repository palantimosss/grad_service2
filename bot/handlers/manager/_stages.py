"""Stage handlers for manager."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.stage_crud import (
    StageCreateParams,
    create_stage,
)
from bot.database.database import get_session
from bot.states.states import StageCreation

logger = logging.getLogger(__name__)

stages_router = Router()

# Skip option text
_SKIP_OPTION = "пропустить"

# Default values
_DEFAULT_ORDER = 0


def _parse_datetime(text: str, fmt: str) -> datetime | None:
    """Parse datetime from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return datetime.strptime(text, fmt).replace(tzinfo=UTC)
    except ValueError:
        return None


def _build_stage_params(stage_data: dict) -> StageCreateParams:
    """Build stage creation params."""
    stage_params: StageCreateParams = {
        "project_id": stage_data["project_id"],
        "title": stage_data["title"],
        "order": stage_data.get("order", _DEFAULT_ORDER),
    }
    if stage_data.get("description"):
        stage_params["description"] = stage_data["description"]
    if stage_data.get("planned_start"):
        stage_params["planned_start"] = stage_data["planned_start"]
    if stage_data.get("planned_end"):
        stage_params["planned_end"] = stage_data["planned_end"]
    return stage_params


@stages_router.callback_query(
    lambda callback: callback.data.startswith("create_stage_"),
)
async def create_stage_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start stage creation."""
    parts = callback.data.split("_")
    proj_id = int(parts[2])
    await state.update_data(project_id=proj_id)
    await callback.message.edit_text(
        "Создание этапа.\nВведите название:",
    )
    await state.set_state(StageCreation.title)


@stages_router.message(StageCreation.title)
async def stage_title(message: types.Message, state: FSMContext) -> None:
    """Process stage title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(StageCreation.description)


@stages_router.message(StageCreation.description)
async def stage_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage description."""
    desc_val: str | None = None
    if message.text != _SKIP_OPTION:
        desc_val = message.text
    await state.update_data(description=desc_val)
    await message.answer("Введите порядок этапа (число):")
    await state.set_state(StageCreation.order)


@stages_router.message(StageCreation.order)
async def stage_order(message: types.Message, state: FSMContext) -> None:
    """Process stage order."""
    try:
        order_val = int(message.text)
    except ValueError:
        await message.answer("Введите число:")
        return
    await state.update_data(order=order_val)
    await message.answer(
        "Плановая дата начала (ДД.ММ.ГГГГ) "
        f"или '{_SKIP_OPTION}':",
    )
    await state.set_state(StageCreation.planned_start)


@stages_router.message(StageCreation.planned_start)
async def stage_start_date(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage start date."""
    start = _parse_datetime(message.text, "%d.%m.%Y")
    if start is None and message.text != _SKIP_OPTION:
        await message.answer("Неверный формат:")
        return
    await state.update_data(planned_start=start)
    await message.answer(
        "Плановая дата окончания (ДД.ММ.ГГГГ) "
        f"или '{_SKIP_OPTION}':",
    )
    await state.set_state(StageCreation.planned_end)


@stages_router.message(StageCreation.planned_end)
async def stage_end_date(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage end date and create stage."""
    end = _parse_datetime(message.text, "%d.%m.%Y")
    if end is None and message.text != _SKIP_OPTION:
        await message.answer("Неверный формат:")
        return
    stage_data = await state.get_data()
    async for session in get_session():
        stage_params = _build_stage_params(stage_data)
        await create_stage(session=session, params=stage_params)
    await message.answer("Этап создан!")
    await state.clear()
