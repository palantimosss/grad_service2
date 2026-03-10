"""Manager handlers package."""

# Import routers for package interface
from bot.handlers.manager._clients import clients_router
from bot.handlers.manager._projects import projects_router
from bot.handlers.manager._router import manager_router
from bot.handlers.manager._stages import stages_router
from bot.handlers.manager._stats import stats_router
from bot.handlers.manager._tasks import tasks_router

__all__ = (
    "clients_router",
    "manager_router",
    "projects_router",
    "stages_router",
    "stats_router",
    "tasks_router",
)
