"""Performer task handlers."""

import logging

from aiogram import Router, types

from bot.database.crud_modules.task_crud import (
    get_task_by_id,
    get_tasks_by_performer_id,
    update_task_status,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import TaskStatus
from bot.keyboards.menus import (
    get_task_actions_keyboard,
    get_tasks_keyboard,
)

logger = logging.getLogger(__name__)

performer_task_router = Router()

_STATUS_MAP = (
    ("pending", "Ожидает"),
    ("in_progress", "В работе"),
    ("review", "На проверке"),
    ("completed", "Завершена"),
    ("cancelled", "Отменена"),
)


def _get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, label in _STATUS_MAP:
        if key == status_value:
            return label
    return status_value


def _get_task_lines(task: object, status_text: str) -> list[str]:
    """Get task info lines."""
    description = task.description or "Нет"
    deadline = task.deadline or "Не установлен"
    return [
        f"<b>{task.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Описание: {description}",
        f"Приоритет: {task.priority}",
        f"Дедлайн: {deadline}",
    ]


def _build_task_text(task: object, status_text: str) -> str:
    """Build task detail text."""
    lines = _get_task_lines(task, status_text)
    return "\n".join(lines)


def _get_callback_data(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def _get_task_id(callback: types.CallbackQuery) -> int:
    """Extract task ID from callback."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[1])


def _get_task_id_from_action(callback: types.CallbackQuery) -> int:
    """Extract task ID from action callback."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[2])


async def _update_task_status_in_db(
    task_id: int,
    status: TaskStatus,
) -> None:
    """Update task status in database."""
    async for session in get_session():
        await update_task_status(session, task_id, status)


async def _show_task_info(callback: types.CallbackQuery) -> None:
    """Show task information."""
    task_id = _get_task_id(callback)
    async for session in get_session():
        task = await get_task_by_id(session, task_id)
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return
        status_text = _get_status_text(task.status.value)
        text = _build_task_text(task, status_text)
        await callback.message.edit_text(
            text,
            reply_markup=get_task_actions_keyboard(task_id, task.status),
        )


@performer_task_router.callback_query(
    lambda callback: callback.data == "my_tasks",
)
async def my_tasks(callback: types.CallbackQuery) -> None:
    """Show performer's tasks."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer("Сначала зарегистрируйтесь", show_alert=True)
            return
        tasks_list = await get_tasks_by_performer_id(session, user.id)
        if not tasks_list:
            await callback.message.edit_text("У вас нет задач.")
            return
        await callback.message.edit_text(
            "Ваши задачи:", reply_markup=get_tasks_keyboard(tasks_list),
        )


@performer_task_router.callback_query(
    lambda callback: callback.data.startswith("task_"),
)
async def task_detail(callback: types.CallbackQuery) -> None:
    """Show task details."""
    callback_data = _get_callback_data(callback)
    if callback_data.startswith("task_start_"):
        task_id = _get_task_id_from_action(callback)
        await _update_task_status_in_db(task_id, TaskStatus.IN_PROGRESS)
        await callback.message.edit_text(f"Задача {task_id} взята в работу.")
        return
    if callback_data.startswith("task_complete_"):
        task_id = _get_task_id_from_action(callback)
        await _update_task_status_in_db(task_id, TaskStatus.COMPLETED)
        await callback.message.edit_text("Задача завершена!")
        return
    await _show_task_info(callback)
