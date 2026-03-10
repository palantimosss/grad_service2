"""Project keyboards: projects list, project actions, project status."""

from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.enums import ProjectStatus, UserRole

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_MENU,
    _BACK_PROJECT,
    _BACK_TEXT,
    _adjust_single,
    _build_single_column_keyboard,
)


def get_projects_keyboard(projects: list) -> InlineKeyboardMarkup:
    """Get projects list keyboard."""
    builder = InlineKeyboardBuilder()
    for project in projects:
        builder.button(
            text=f"📁 {project.title}",
            callback_data=f"project_{project.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def _get_project_action_buttons(
    project_id: int, role: UserRole,
) -> list[tuple[str, str]]:
    """Get project action buttons based on role."""
    if role == UserRole.CLIENT:
        return [
            ("Загрузить документ", f"upload_doc_{project_id}"),
            ("Обратная связь", f"feedback_{project_id}"),
            (_BACK_TEXT, _BACK_MENU),
        ]
    if role == UserRole.MANAGER:
        return [
            ("Создать задачу", f"create_task_{project_id}"),
            ("Создать этап", f"create_stage_{project_id}"),
            ("Создать встречу", f"create_meeting_{project_id}"),
            ("Статус проекта", f"project_status_{project_id}"),
            (_BACK_TEXT, _BACK_MENU),
        ]
    # PERFORMER
    return [
        ("Загрузить документ", f"upload_doc_{project_id}"),
        (_BACK_TEXT, _BACK_MENU),
    ]


def get_project_actions_keyboard(
    project_id: int, role: UserRole,
) -> InlineKeyboardMarkup:
    """Get project actions keyboard."""
    buttons = _get_project_action_buttons(project_id, role)
    return _build_single_column_keyboard(buttons)


def get_project_status_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Get project status change keyboard."""
    builder = InlineKeyboardBuilder()
    for status in ProjectStatus:
        builder.button(
            text=status.value.replace("_", " ").title(),
            callback_data=f"set_status_{project_id}_{status.value}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_PROJECT)
    builder.adjust(2)
    return builder.as_markup()
