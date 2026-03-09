"""Manager handlers package."""

from aiogram import Router

from bot.handlers.manager._clients import clients_router
from bot.handlers.manager._projects import projects_router
from bot.handlers.manager._stages import stages_router
from bot.handlers.manager._stats import stats_router
from bot.handlers.manager._tasks import tasks_router

manager_router = Router()

manager_router.include_router(projects_router)
manager_router.include_router(tasks_router)
manager_router.include_router(stages_router)
manager_router.include_router(clients_router)
manager_router.include_router(stats_router)
