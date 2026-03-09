"""Performer project handlers."""

import logging

from aiogram import Router, types

from bot.database.crud_modules.project_crud import (
    get_projects_by_manager_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.keyboards.menus import get_projects_keyboard

logger = logging.getLogger(__name__)

performer_project_router = Router()


@performer_project_router.callback_query(lambda c: c.data == "projects")
async def projects(callback: types.CallbackQuery) -> None:
    """Show projects for performer."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(
                "Сначала зарегистрируйтесь", show_alert=True,
            )
            return
        projects_list = await get_projects_by_manager_id(session, user.id)
        if not projects_list:
            await callback.message.edit_text("У вас нет проектов.")
            return
        await callback.message.edit_text(
            "Ваши проекты:",
            reply_markup=get_projects_keyboard(projects_list),
        )
