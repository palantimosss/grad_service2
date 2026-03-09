"""Task handlers for manager."""

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.task_crud import (
    get_tasks_by_project_id,
)
from bot.database.crud_modules.user_crud import (
    get_user_by_telegram_id,
    get_users_by_role,
)
from bot.database.database import get_session
from bot.database.models.enums import UserRole
from bot.handlers.manager._tasks_helpers import (
    build_performers_text,
    create_task_in_db,
    get_project_id_from_callback,
    get_skip_option,
    parse_datetime,
)
from bot.keyboards.menus import get_tasks_keyboard
from bot.states.states import TaskCreation

logger = logging.getLogger(__name__)

tasks_router = Router()

_SKIP_OPTION = get_skip_option()
_DEFAULT_TASK_PRIORITY = 3


async def _fetch_performers(session: object) -> list:
    """Fetch performers from database."""
    return await get_users_by_role(session, UserRole.PERFORMER)


@tasks_router.callback_query(
    lambda callback: callback.data == "all_tasks",
)
async def all_tasks(callback: types.CallbackQuery) -> None:
    """Show all tasks."""
    async for session in get_session():
        tasks_list = await get_tasks_by_project_id(session, 0)
        if not tasks_list:
            await callback.message.edit_text("Задач нет.")
            return
        await callback.message.edit_text(
            "Все задачи:", reply_markup=get_tasks_keyboard(tasks_list),
        )


@tasks_router.callback_query(
    lambda callback: callback.data.startswith("create_task_"),
)
async def create_task_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start task creation."""
    proj_id = get_project_id_from_callback(callback)
    await state.update_data(project_id=proj_id)
    await callback.message.edit_text(
        "Создание задачи.\nВведите название:",
    )
    await state.set_state(TaskCreation.title)


@tasks_router.message(TaskCreation.title)
async def task_title(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(TaskCreation.description)


async def _handle_no_performers(
    message: types.Message,
    state: FSMContext,
) -> bool:
    """Handle case when no performers found."""
    async for session in get_session():
        performers = await _fetch_performers(session)
        if not performers:
            await message.answer("Нет исполнителей.")
            await state.clear()
            return True
        text = build_performers_text(performers)
        await message.answer(text)
        await state.set_state(TaskCreation.performer)
        return False
    return True


@tasks_router.message(TaskCreation.description)
async def task_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task description."""
    desc_val: str | None = None
    if message.text != _SKIP_OPTION:
        desc_val = message.text
    await state.update_data(description=desc_val)
    should_stop = await _handle_no_performers(message, state)
    if should_stop:
        return


@tasks_router.message(TaskCreation.performer)
async def task_performer(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task performer."""
    try:
        performer_id = int(message.text)
    except ValueError:
        await message.answer("Введите числовой ID:")
        return
    await state.update_data(performer_id=performer_id)
    await message.answer(
        "Введите дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ) "
        f"или '{_SKIP_OPTION}':",
    )
    await state.set_state(TaskCreation.deadline)


@tasks_router.message(TaskCreation.deadline)
async def task_deadline(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task deadline."""
    deadline = parse_datetime(message.text, "%d.%m.%Y %H:%M")
    if deadline is None and message.text != _SKIP_OPTION:
        await message.answer("Неверный формат:")
        return
    await state.update_data(deadline=deadline)
    await message.answer("Введите приоритет (1-5) или 'пропустить':")
    await state.set_state(TaskCreation.priority)


async def _finalize_task_creation(
    message: types.Message,
    task_data: dict,
    priority: int,
) -> None:
    """Finalize task creation in database."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await create_task_in_db(session, user.id, task_data, priority)


@tasks_router.message(TaskCreation.priority)
async def task_priority(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task priority and create task."""
    priority_val = _DEFAULT_TASK_PRIORITY
    if message.text != _SKIP_OPTION:
        try:
            priority_val = int(message.text)
        except ValueError:
            await message.answer("Введите число 1-5:")
            return
    task_data = await state.get_data()
    await _finalize_task_creation(message, task_data, priority_val)
    await message.answer("Задача создана!")
    await state.clear()
