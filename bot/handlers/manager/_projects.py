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
from bot.keyboards.menus import (
    get_project_actions_keyboard,
    get_projects_keyboard,
    get_yes_no_keyboard,
)

logger = logging.getLogger(__name__)

projects_router = Router()

# Status map for display (immutable tuple)
_STATUS_MAP = (
    ("draft", "Черновик"),
    ("pending", "На регистрации"),
    ("registered", "Зарегистрирован"),
    ("in_progress", "В работе"),
    ("on_hold", "Приостановлен"),
    ("completed", "Завершён"),
    ("archived", "Архив"),
)


def _get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, label in _STATUS_MAP:
        if key == status_value:
            return label
    return status_value


def _build_project_text(project: object, status_text: str) -> str:
    """Build project detail text."""
    client_name = (
        project.client.first_name if project.client else "Не назначен"
    )
    manager_name = (
        project.manager.first_name if project.manager else "Не назначен"
    )
    return "\n".join([
        f"<b>{project.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Клиент: {client_name}",
        f"Руководитель: {manager_name}",
        f"Описание: {project.description or 'Нет'}",
        f"Дедлайн: {project.deadline or 'Не установлен'}",
        f"Бюджет: {project.budget or 'Не указан'}",
    ])


def _get_callback_data(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def _get_project_id_from_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from callback data."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[1])


def _get_project_id_from_status_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from status callback data."""
    parts = _get_callback_data(callback).split("_")
    return int(parts[2])


def _get_status_from_callback(callback: types.CallbackQuery) -> ProjectStatus:
    """Extract status from callback data."""
    parts = _get_callback_data(callback).split("_")
    return ProjectStatus(parts[3])


@projects_router.callback_query(lambda c: c.data == "all_projects")
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


@projects_router.callback_query(lambda c: c.data == "pending_projects")
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


@projects_router.callback_query(lambda c: c.data.startswith("project_"))
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    proj_id = _get_project_id_from_callback(callback)
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        project = await get_project_by_id(session, proj_id)
        if not project:
            await callback.answer("Проект не найден", show_alert=True)
            return
        status_text = _get_status_text(project.status.value)
        text = _build_project_text(project, status_text)
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


@projects_router.callback_query(lambda c: c.data == "yes")
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


@projects_router.callback_query(
    lambda c: c.data.startswith("project_status_"),
)
async def change_status_start(callback: types.CallbackQuery) -> None:
    """Start changing project status."""
    proj_id = _get_project_id_from_status_callback(callback)
    await callback.message.edit_text(
        "Выберите новый статус проекта:",
        reply_markup=get_project_actions_keyboard(proj_id),
    )


@projects_router.callback_query(lambda c: c.data.startswith("set_status_"))
async def set_project_status(callback: types.CallbackQuery) -> None:
    """Set project status."""
    proj_id = _get_project_id_from_status_callback(callback)
    status = _get_status_from_callback(callback)
    async for session in get_session():
        await update_project_status(session, proj_id, status)
    await callback.message.edit_text(
        f"Статус проекта изменён на {status.value}",
    )
    await callback.message.answer("Нажмите /menu для возврата в меню")
