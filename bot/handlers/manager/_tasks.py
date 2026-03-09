"""Task handlers for manager."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.task_crud import (
    TaskCreateParams,
    create_task,
    get_tasks_by_project_id,
)
from bot.database.crud_modules.user_crud import (
    get_user_by_telegram_id,
    get_users_by_role,
)
from bot.database.database import get_session
from bot.database.models.enums import TaskStatus, UserRole
from bot.keyboards.menus import get_tasks_keyboard
from bot.states.states import TaskCreation

logger = logging.getLogger(__name__)

tasks_router = Router()

# Skip option text
_SKIP_OPTION = "пропустить"

# Default values
_DEFAULT_TASK_PRIORITY = 3


def _build_performers_text(performers: list) -> str:
    """Build performers selection text."""
    lines = ["Выберите исполнителя (ID):"]
    lines.extend(
        f"{performer.id} - {performer.first_name}"
        for performer in performers
    )
    lines.append("Или введите ID вручную:")
    return "\n".join(lines)


def _parse_datetime(text: str, fmt: str) -> datetime | None:
    """Parse datetime from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return datetime.strptime(text, fmt).replace(tzinfo=UTC)
    except ValueError:
        return None


def _build_task_params(
    task_data: dict,
    user_id: int,
    priority: int,
) -> TaskCreateParams:
    """Build task creation params."""
    task_params: TaskCreateParams = {
        "project_id": task_data["project_id"],
        "title": task_data["title"],
        "performer_id": task_data.get("performer_id"),
        "manager_id": user_id,
        "priority": priority,
        "status": TaskStatus.PENDING,
    }
    if task_data.get("description"):
        task_params["description"] = task_data["description"]
    if task_data.get("deadline"):
        task_params["deadline"] = task_data["deadline"]
    return task_params


def _get_callback_data(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def _get_project_id_from_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from callback data."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[2])


async def _fetch_performers(session: object) -> list:
    """Fetch performers from database."""
    return await get_users_by_role(session, UserRole.PERFORMER)


async def _create_task_in_db(
    session: object,
    user_id: int,
    task_data: dict,
    priority: int,
) -> None:
    """Create task in database."""
    task_params = _build_task_params(task_data, user_id, priority)
    await create_task(session=session, params=task_params)


@tasks_router.callback_query(lambda c: c.data == "all_tasks")
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
    lambda c: c.data.startswith("create_task_"),
)
async def create_task_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start task creation."""
    proj_id = _get_project_id_from_callback(callback)
    await state.update_data(project_id=proj_id)
    await callback.message.edit_text(
        "Создание задачи.\nВведите название:",
    )
    await state.set_state(TaskCreation.title)


@tasks_router.message(TaskCreation.title)
async def task_title(message: types.Message, state: FSMContext) -> None:
    """Process task title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(TaskCreation.description)


async def _handle_no_performers(
    message: types.Message,
    state: FSMContext,
) -> bool:
    """Handle case when no performers found. Returns True if should stop."""
    async for session in get_session():
        performers = await _fetch_performers(session)
        if not performers:
            await message.answer("Нет исполнителей.")
            await state.clear()
            return True
        text = _build_performers_text(performers)
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
async def task_performer(message: types.Message, state: FSMContext) -> None:
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
async def task_deadline(message: types.Message, state: FSMContext) -> None:
    """Process task deadline."""
    deadline = _parse_datetime(message.text, "%d.%m.%Y %H:%M")
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
        await _create_task_in_db(session, user.id, task_data, priority)


@tasks_router.message(TaskCreation.priority)
async def task_priority(message: types.Message, state: FSMContext) -> None:
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
