"""Performer handlers package."""

from aiogram import Router

from bot.handlers._performer_docs import document_upload_router
from bot.handlers._performer_projects import performer_project_router
from bot.handlers._performer_tasks import performer_task_router

performer_router = Router()

performer_router.include_router(performer_task_router)
performer_router.include_router(document_upload_router)
performer_router.include_router(performer_project_router)
