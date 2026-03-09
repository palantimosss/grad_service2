"""Notifications and meetings handlers package."""

from aiogram import Router

from bot.handlers._meeting_creation import meeting_creation_router
from bot.handlers._meeting_detail import meeting_detail_router
from bot.handlers._notifications import notification_router

notifications_router = Router()

notifications_router.include_router(meeting_creation_router)
notifications_router.include_router(meeting_detail_router)
notifications_router.include_router(notification_router)
