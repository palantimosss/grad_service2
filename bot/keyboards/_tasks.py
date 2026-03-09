"""Task keyboards: tasks list, task actions."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.enums import TaskStatus

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_MENU,
    _BACK_TASKS,
    _BACK_TEXT,
    _adjust_single,
    _build_single_column_keyboard,
)


def _get_task_emoji(status: TaskStatus) -> str:
    """Get emoji for task status."""
    return "⏳" if status == TaskStatus.PENDING else "✅"


def get_tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Get tasks list keyboard."""
    builder = InlineKeyboardBuilder()
    for task in tasks:
        emoji = _get_task_emoji(task.status)
        builder.button(
            text=f"{emoji} {task.title}",
            callback_data=f"task_{task.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def _get_task_action_buttons(
    task_id: int, status: TaskStatus,
) -> list[tuple[str, str]]:
    """Get task action buttons based on status."""
    buttons = []
    if status == TaskStatus.PENDING:
        buttons.append(("Взять в работу", f"task_start_{task_id}"))
    elif status == TaskStatus.IN_PROGRESS:
        buttons.append(("Завершить", f"task_complete_{task_id}"))
    buttons.append(("Загрузить документ", f"upload_doc_task_{task_id}"))
    buttons.append((_BACK_TEXT, _BACK_TASKS))
    return buttons


def get_task_actions_keyboard(
    task_id: int, status: TaskStatus,
) -> InlineKeyboardMarkup:
    """Get task actions keyboard."""
    buttons = _get_task_action_buttons(task_id, status)
    return _build_single_column_keyboard(buttons)
