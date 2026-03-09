"""Common handlers package."""

from aiogram import Router

from bot.handlers._help import help_router
from bot.handlers._profile import profile_router
from bot.handlers.common import registration_router

common_router = Router()

common_router.include_router(registration_router)
common_router.include_router(profile_router)
common_router.include_router(help_router)
