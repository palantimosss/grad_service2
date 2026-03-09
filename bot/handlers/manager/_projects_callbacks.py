"""Project handlers helper functions - callback utilities."""

from typing import TYPE_CHECKING

from bot.database.models.enums import ProjectStatus

if TYPE_CHECKING:
    from aiogram import types


def get_callback_data_str(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def get_project_id_from_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from callback data."""
    parts = get_callback_data_str(callback).split("_")
    return int(parts[1])


def get_project_id_from_status_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from status callback data."""
    parts = get_callback_data_str(callback).split("_")
    return int(parts[2])


def get_status_from_callback(callback: types.CallbackQuery) -> ProjectStatus:
    """Extract status from callback data."""
    parts = get_callback_data_str(callback).split("_")
    return ProjectStatus(parts[3])


# Predicate functions for callback filtering
def is_all_projects(callback: types.CallbackQuery) -> bool:
    """Check if callback is for all projects."""
    return callback.data == "all_projects"


def is_pending_projects(callback: types.CallbackQuery) -> bool:
    """Check if callback is for pending projects."""
    return callback.data == "pending_projects"


def is_project_detail(callback: types.CallbackQuery) -> bool:
    """Check if callback is for project detail."""
    return callback.data.startswith("project_")


def is_yes_callback(callback: types.CallbackQuery) -> bool:
    """Check if callback is yes."""
    return callback.data == "yes"


def is_project_status(callback: types.CallbackQuery) -> bool:
    """Check if callback is for project status."""
    return callback.data.startswith("project_status_")


def is_set_status(callback: types.CallbackQuery) -> bool:
    """Check if callback is for set status."""
    return callback.data.startswith("set_status_")
