"""Client handlers: projects."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.project_crud import (
    create_project,
    get_project_by_id,
    get_projects_by_client_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import ProjectStatus
from bot.handlers._client_helpers import (
    format_project_text,
    get_skip_option,
    parse_budget,
    parse_deadline,
)
from bot.keyboards.menus import (
    get_back_keyboard,
    get_project_actions_keyboard,
    get_projects_keyboard,
)
from bot.states.states import ProjectCreation

logger = logging.getLogger(__name__)

client_projects_router = Router()

_PROJECT_ID_KEY = "project_id"
_SKIP_OPTION = get_skip_option()


async def _create_project_in_db(
    session: object,
    project_data: dict,
    user_id: int,
) -> None:
    """Create project in database."""
    create_params = {
        "title": project_data["title"],
        "client_id": user_id,
        "status": ProjectStatus.DRAFT,
    }
    if project_data.get("description"):
        create_params["description"] = project_data["description"]
    if project_data.get("deadline"):
        create_params["deadline"] = project_data["deadline"]
    if project_data.get("budget"):
        create_params["budget"] = project_data["budget"]
    await create_project(session=session, params=create_params)


@client_projects_router.callback_query(
    lambda callback: callback.data == "my_projects",
)
async def my_projects(callback: types.CallbackQuery) -> None:
    """Show client's projects."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer("Сначала зарегистрируйтесь", show_alert=True)
            return
        projects = await get_projects_by_client_id(session, user.id)

        if not projects:
            await callback.message.edit_text(
                "У вас пока нет проектов.\nСоздайте новый проект:",
                reply_markup=get_back_keyboard("create_project"),
            )
            return
        await callback.message.edit_text(
            "Ваши проекты:", reply_markup=get_projects_keyboard(projects),
        )


@client_projects_router.callback_query(
    lambda callback: callback.data == "create_project",
)
async def create_project_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start project creation."""
    await callback.message.edit_text(
        "Создание нового проекта.\nВведите название проекта:",
    )
    await state.set_state(ProjectCreation.title)


@client_projects_router.message(ProjectCreation.title)
async def project_title(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(ProjectCreation.description)


@client_projects_router.message(ProjectCreation.description)
async def project_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project description."""
    desc_val: str | None = None
    if message.text != _SKIP_OPTION:
        desc_val = message.text
    await state.update_data(description=desc_val)
    await message.answer(
        "Введите дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ) "
        f"или '{_SKIP_OPTION}':",
    )
    await state.set_state(ProjectCreation.deadline)


@client_projects_router.message(ProjectCreation.deadline)
async def project_deadline(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project deadline."""
    deadline = parse_deadline(message.text)
    if deadline is None and message.text != _SKIP_OPTION:
        await message.answer("Неверный формат:")
        return
    await state.update_data(deadline=deadline)
    await message.answer("Введите бюджет (или 'пропустить'):")
    await state.set_state(ProjectCreation.budget)


@client_projects_router.message(ProjectCreation.budget)
async def project_budget(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project budget and create project."""
    budget = parse_budget(message.text)
    if budget is None and message.text != _SKIP_OPTION:
        await message.answer("Введите число:")
        return
    await state.update_data(budget=budget)
    await _finalize_project_creation(message, state)


async def _finalize_project_creation(
    message: types.Message,
    state: FSMContext,
) -> None:
    """Finalize project creation in database."""
    project_data = await state.get_data()
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await _create_project_in_db(session, project_data, user.id)
    await message.answer("Проект создан!")
    await state.clear()


@client_projects_router.callback_query(
    lambda callback: callback.data.startswith("project_"),
)
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    parts = callback.data.split("_")
    project_id = int(parts[1])
    async for session in get_session():
        await _show_project_detail(callback, session, project_id)


async def _show_project_detail(
    callback: types.CallbackQuery,
    session: object,
    project_id: int,
) -> None:
    """Show project detail in a session."""
    user = await get_user_by_telegram_id(session, callback.from_user.id)
    project = await get_project_by_id(session, project_id)
    if not project:
        await callback.answer("Проект не найден", show_alert=True)
        return
    text = format_project_text(project)
    await callback.message.edit_text(
        text,
        reply_markup=get_project_actions_keyboard(project_id, user.role),
    )
