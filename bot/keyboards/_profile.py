"""Profile keyboards: role, main menu, profile, edit profile."""

from typing import TYPE_CHECKING

from bot.database.models.enums import UserRole

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_MENU,
    _BACK_PROFILE,
    _BACK_TEXT,
    _build_double_column_keyboard,
    _build_single_column_keyboard,
)


def get_role_keyboard() -> InlineKeyboardMarkup:
    """Get role selection keyboard."""
    return _build_single_column_keyboard([
        ("Клиент", "role_client"),
        ("Руководитель", "role_manager"),
        ("Исполнитель", "role_performer"),
    ])


def get_main_menu_keyboard(role: UserRole) -> InlineKeyboardMarkup:
    """Get main menu keyboard based on role."""
    if role == UserRole.CLIENT:
        return _build_single_column_keyboard([
            ("Мои проекты", "my_projects"),
            ("Создать проект", "create_project"),
            ("Профиль", "profile"),
        ])
    if role == UserRole.MANAGER:
        return _build_single_column_keyboard([
            ("Все проекты", "all_projects"),
            ("Заявки", "pending_projects"),
            ("Задачи", "all_tasks"),
            ("Клиенты", "clients"),
            ("Статистика", "statistics"),
            ("Профиль", "profile"),
        ])
    # PERFORMER
    return _build_single_column_keyboard([
        ("Мои задачи", "my_tasks"),
        ("Проекты", "projects"),
        ("Профиль", "profile"),
    ])


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Get profile keyboard."""
    return _build_double_column_keyboard([
        ("Редактировать", "edit_profile"),
        (_BACK_TEXT, _BACK_MENU),
    ])


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Get edit profile keyboard."""
    return _build_double_column_keyboard([
        ("Телефон", "edit_phone"),
        ("Email", "edit_email"),
        ("Должность", "edit_position"),
        (_BACK_TEXT, _BACK_PROFILE),
    ])
