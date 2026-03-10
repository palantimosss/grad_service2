"""Project handlers for manager - CRUD imports."""

from bot.database.crud_modules.project_crud import (
    assign_manager_to_project,
    get_all_projects,
    get_pending_projects,
    get_project_by_id,
    update_project_status,
)

__all__ = (
    "assign_manager_to_project",
    "get_all_projects",
    "get_pending_projects",
    "get_project_by_id",
    "update_project_status",
)
