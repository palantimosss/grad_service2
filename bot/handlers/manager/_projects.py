"""Project handlers for manager."""

import logging

from aiogram import F, Router, types

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

# String length limits
_TITLE_LIMIT = 50
_NAME_LIMIT = 30


def _get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, value in _STATUS_MAP:
        if key == status_value:
            return value
    return status_value


def _build_project_text(project: object, status_text: str) -> str:
    """Build project detail text."""
    client_name = "Не назначен"
    if project.client:
        client_name = project.client.first_name
    manager_name = "Не назначен"
    if project.manager:
        manager_name = project.manager.first_name
    desc_val = project.description or "Нет"
    deadline_val = project.deadline or "Не установлен"
    budget_val = project.budget or "Не указан"
    lines = [
        f"<b>{project.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Клиент: {client_name}",
        f"Руководитель: {manager_name}",
        f"Описание: {desc_val}",
        f"Дедлайн: {deadline_val}",
        f"Бюджет: {budget_val}",
    ]
    return "\n".join(lines)


@projects_router.callback_query(F.data == "all_projects")
async def all_projects(callback: types.CallbackQuery) -> None:
    """Show all projects."""
    async for session in get_session():
        projects = await get_all_projects(session)
        if not projects:
            await callback.message.edit_text("Проектов нет.")
            return
        await callback.message.edit_text(
            "Все проекты:", reply_markup=get_projects_keyboard(projects),
        )


@projects_router.callback_query(F.data == "pending_projects")
async def pending_projects(callback: types.CallbackQuery) -> None:
    """Show pending projects."""
    async for session in get_session():
        projects = await get_pending_projects(session)
        if not projects:
            await callback.message.edit_text("Заявок на регистрацию нет.")
            return
        await callback.message.edit_text(
            "Заявки на регистрацию:",
            reply_markup=get_projects_keyboard(projects),
        )


@projects_router.callback_query(F.data.startswith("project_"))
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    parts = callback.data.split("_")
    proj_id = int(parts[1])
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


@projects_router.callback_query(F.data == "yes")
async def register_project(callback: types.CallbackQuery) -> None:
    """Register pending project."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        projects = await get_pending_projects(session)
        if projects:
            project = projects[0]
            await assign_manager_to_project(session, project.id, user.id)
            await callback.message.edit_text(
                f"Проект '{project.title}' зарегистрирован.",
            )


@projects_router.callback_query(F.data.startswith("project_status_"))
async def change_status_start(callback: types.CallbackQuery) -> None:
    """Start changing project status."""
    parts = callback.data.split("_")
    proj_id = int(parts[2])
    await callback.message.edit_text(
        "Выберите новый статус проекта:",
        reply_markup=get_project_actions_keyboard(proj_id),
    )


@projects_router.callback_query(F.data.startswith("set_status_"))
async def set_project_status(callback: types.CallbackQuery) -> None:
    """Set project status."""
    parts = callback.data.split("_")
    proj_id = int(parts[2])
    status = ProjectStatus(parts[3])
    async for session in get_session():
        await update_project_status(session, proj_id, status)
    await callback.message.edit_text(
        f"Статус проекта изменён на {status.value}",
    )
    await callback.message.answer("Нажмите /menu для возврата в меню")
