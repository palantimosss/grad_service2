"""Project handlers for manager."""

import logging

from aiogram import Router, types

from bot.database.crud_modules.project_crud import (
    assign_manager_to_project,
    get_all_projects,
    get_pending_projects,
    get_project_by_id,
    update_project_status,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import ProjectStatus
from bot.handlers.manager._projects_callbacks import (
    get_project_id_from_callback,
    get_project_id_from_status_callback,
    get_status_from_callback,
    is_all_projects,
    is_pending_projects,
    is_project_detail,
    is_project_status,
    is_set_status,
    is_yes_callback,
)
from bot.handlers.manager._projects_helpers import (
    build_project_text,
    get_status_text,
)
from bot.keyboards.menus import (
    get_project_actions_keyboard,
    get_projects_keyboard,
    get_yes_no_keyboard,
)

logger = logging.getLogger(__name__)

projects_router = Router()


@projects_router.callback_query(is_all_projects)
async def all_projects(callback: types.CallbackQuery) -> None:
    """Show all projects."""
    async for session in get_session():
        projects_list = await get_all_projects(session)
        if not projects_list:
            await callback.message.edit_text("Проектов нет.")
            return
        await callback.message.edit_text(
            "Все проекты:", reply_markup=get_projects_keyboard(projects_list),
        )


@projects_router.callback_query(is_pending_projects)
async def pending_projects(callback: types.CallbackQuery) -> None:
    """Show pending projects."""
    async for session in get_session():
        projects_list = await get_pending_projects(session)
        if not projects_list:
            await callback.message.edit_text("Заявок на регистрацию нет.")
            return
        await callback.message.edit_text(
            "Заявки на регистрацию:",
            reply_markup=get_projects_keyboard(projects_list),
        )


@projects_router.callback_query(is_project_detail)
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    proj_id = get_project_id_from_callback(callback)
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        project = await get_project_by_id(session, proj_id)
        if not project:
            await callback.answer("Проект не найден", show_alert=True)
            return
        status_text = get_status_text(project.status.value)
        text = build_project_text(project, status_text)
        if project.status == ProjectStatus.PENDING:
            await callback.message.edit_text(
                text, reply_markup=get_yes_no_keyboard(),
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=get_project_actions_keyboard(
                    proj_id, user.role,
                ),
            )


@projects_router.callback_query(is_yes_callback)
async def register_project(callback: types.CallbackQuery) -> None:
    """Register pending project."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        projects_list = await get_pending_projects(session)
        if projects_list:
            project = projects_list[0]
            await assign_manager_to_project(session, project.id, user.id)
            await callback.message.edit_text(
                f"Проект '{project.title}' зарегистрирован.",
            )


@projects_router.callback_query(is_project_status)
async def change_status_start(callback: types.CallbackQuery) -> None:
    """Start changing project status."""
    proj_id = get_project_id_from_status_callback(callback)
    await _show_status_selection(callback.message, proj_id)


async def _show_status_selection(message: types.Message, proj_id: int) -> None:
    """Show status selection keyboard."""
    await message.edit_text(
        "Выберите новый статус проекта:",
        reply_markup=get_project_actions_keyboard(proj_id),
    )


@projects_router.callback_query(is_set_status)
async def set_project_status(callback: types.CallbackQuery) -> None:
    """Set project status."""
    proj_id = get_project_id_from_status_callback(callback)
    status = get_status_from_callback(callback)
    async for session in get_session():
        await update_project_status(session, proj_id, status)
    await callback.message.edit_text(
        f"Статус проекта изменён на {status.value}",
    )
    await callback.message.answer("Нажмите /menu для возврата в меню")
