"""Statistics CRUD operations."""

from bot.database.crud_modules.statistics_crud import (
    get_manager_projects_count,
    get_performer_tasks_count,
    get_projects_count_by_status,
    get_tasks_count_by_status,
    get_total_projects_count,
    get_total_tasks_count,
    get_total_users_count,
    get_users_count_by_role,
)

__all__ = (  # noqa: WPS410
    "get_manager_projects_count",
    "get_performer_tasks_count",
    "get_projects_count_by_status",
    "get_tasks_count_by_status",
    "get_total_projects_count",
    "get_total_tasks_count",
    "get_total_users_count",
    "get_users_count_by_role",
)
