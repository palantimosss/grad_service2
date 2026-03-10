"""Project CRUD operations."""

from bot.database.crud_modules._project_read import (
    get_all_projects,
    get_pending_projects,
    get_project_by_id,
    get_projects_by_client_id,
    get_projects_by_manager_id,
)
from bot.database.crud_modules.project_crud import (
    assign_manager_to_project,
    create_project,
    delete_project,
    update_project_status,
)

__all__ = (   # noqa: WPS410
    "assign_manager_to_project",
    "create_project",
    "delete_project",
    "get_all_projects",
    "get_pending_projects",
    "get_project_by_id",
    "get_projects_by_client_id",
    "get_projects_by_manager_id",
    "update_project_status",
)
