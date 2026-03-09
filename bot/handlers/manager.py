"""Manager handlers: projects, tasks, clients, statistics."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import F, Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.client_company_crud import (
    CompanyCreateParams,
    create_company,
    get_all_companies,
)
from bot.database.crud_modules.project_crud import (
    assign_manager_to_project,
    get_all_projects,
    get_pending_projects,
    get_project_by_id,
    update_project_status,
)
from bot.database.crud_modules.stage_crud import (
    StageCreateParams,
    create_stage,
)
from bot.database.crud_modules.statistics_crud import (
    get_projects_count_by_status,
    get_tasks_count_by_status,
    get_users_count_by_role,
)
from bot.database.crud_modules.task_crud import (
    TaskCreateParams,
    create_task,
    get_tasks_by_project_id,
)
from bot.database.crud_modules.user_crud import (
    get_user_by_telegram_id,
    get_users_by_role,
)
from bot.database.database import get_session
from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole
from bot.keyboards.menus import (
    get_back_keyboard,
    get_clients_keyboard,
    get_project_actions_keyboard,
    get_project_status_keyboard,
    get_projects_keyboard,
    get_tasks_keyboard,
    get_yes_no_keyboard,
)
from bot.states.states import CompanyCreation, StageCreation, TaskCreation

logger = logging.getLogger(__name__)

manager_router = Router()

STATUS_MAP = {
    "draft": "Черновик",
    "pending": "На регистрации",
    "registered": "Зарегистрирован",
    "in_progress": "В работе",
    "on_hold": "Приостановлен",
    "completed": "Завершён",
    "archived": "Архив",
}


def _build_project_text(project: object, status_text: str) -> str:
    """Build project detail text."""
    client_name = "Не назначен"
    if project.client:
        client_name = project.client.first_name
    manager_name = "Не назначен"
    if project.manager:
        manager_name = project.manager.first_name
    desc = project.description or "Нет"
    deadline = project.deadline or "Не установлен"
    budget = project.budget or "Не указан"
    lines = [
        f"<b>{project.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Клиент: {client_name}",
        f"Руководитель: {manager_name}",
        f"Описание: {desc}",
        f"Дедлайн: {deadline}",
        f"Бюджет: {budget}",
    ]
    return "\n".join(lines)


def _build_performers_text(performers: list) -> str:
    """Build performers selection text."""
    lines = ["Выберите исполнителя (ID):"]
    lines.extend(f"{p.id} - {p.first_name}" for p in performers)
    lines.append("Или введите ID вручную:")
    return "\n".join(lines)


def _build_stats_text(
    projects_stats: dict,
    tasks_stats: dict,
    users_stats: dict,
) -> str:
    """Build statistics text."""
    lines = ["<b>Статистика</b>", "", "<b>Проекты:</b>"]
    for status, count in projects_stats.items():
        lines.append(f"  {status.value}: {count}")
    lines.append("")
    lines.append("<b>Задачи:</b>")
    for status, count in tasks_stats.items():
        lines.append(f"  {status.value}: {count}")
    lines.append("")
    lines.append("<b>Пользователи:</b>")
    for role, count in users_stats.items():
        lines.append(f"  {role.value}: {count}")
    return "\n".join(lines)


def _parse_datetime(text: str, fmt: str) -> datetime | None:
    """Parse datetime from text."""
    if text == "пропустить":
        return None
    try:
        return datetime.strptime(text, fmt).replace(tzinfo=UTC)
    except ValueError:
        return None


def _build_task_params(
    data: dict,
    user_id: int,
    priority: int,
) -> TaskCreateParams:
    """Build task creation params."""
    params: TaskCreateParams = {
        "project_id": data["project_id"],
        "title": data["title"],
        "performer_id": data.get("performer_id"),
        "manager_id": user_id,
        "priority": priority,
        "status": TaskStatus.PENDING,
    }
    if data.get("description"):
        params["description"] = data["description"]
    if data.get("deadline"):
        params["deadline"] = data["deadline"]
    return params


def _build_stage_params(data: dict) -> StageCreateParams:
    """Build stage creation params."""
    params: StageCreateParams = {
        "project_id": data["project_id"],
        "title": data["title"],
        "order": data["order"],
    }
    if data.get("description"):
        params["description"] = data["description"]
    if data.get("planned_start"):
        params["planned_start"] = data["planned_start"]
    if data.get("planned_end"):
        params["planned_end"] = data["planned_end"]
    return params


def _build_company_params(data: dict) -> CompanyCreateParams:
    """Build company creation params."""
    params: CompanyCreateParams = {"name": data["name"]}
    for key in ["inn", "kpp", "address", "phone", "email", "website"]:
        if data.get(key):
            params[key] = data[key]  # type: ignore[literal-required]
    return params


@manager_router.callback_query(F.data == "all_projects")
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


@manager_router.callback_query(F.data == "pending_projects")
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


@manager_router.callback_query(F.data.startswith("project_"))
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    project_id = int(callback.data.split("_")[1])
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        project = await get_project_by_id(session, project_id)
        if not project:
            await callback.answer("Проект не найден", show_alert=True)
            return
        status_text = STATUS_MAP.get(
            project.status.value, project.status.value,
        )
        text = _build_project_text(project, status_text)
        if project.status == ProjectStatus.PENDING:
            await callback.message.edit_text(
                text, reply_markup=get_yes_no_keyboard(),
            )
        else:
            await callback.message.edit_text(
                text,
                reply_markup=get_project_actions_keyboard(
                    project_id, user.role,
                ),
            )


@manager_router.callback_query(F.data == "yes")
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


@manager_router.callback_query(F.data.startswith("project_status_"))
async def change_status_start(callback: types.CallbackQuery) -> None:
    """Start changing project status."""
    project_id = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "Выберите новый статус проекта:",
        reply_markup=get_project_status_keyboard(project_id),
    )


@manager_router.callback_query(F.data.startswith("set_status_"))
async def set_project_status(callback: types.CallbackQuery) -> None:
    """Set project status."""
    parts = callback.data.split("_")
    project_id = int(parts[2])
    status = ProjectStatus(parts[3])
    async for session in get_session():
        await update_project_status(session, project_id, status)
    await callback.message.edit_text(
        f"Статус проекта изменён на {status.value}",
    )
    await callback.message.answer("Нажмите /menu для возврата в меню")


@manager_router.callback_query(F.data.startswith("create_task_"))
async def create_task_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start task creation."""
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text(
        "Создание задачи.\nВведите название:",
    )
    await state.set_state(TaskCreation.title)


@manager_router.message(TaskCreation.title)
async def task_title(message: types.Message, state: FSMContext) -> None:
    """Process task title."""
    await state.update_data(title=message.text)
    await message.answer("Введите описание (или 'пропустить'):")
    await state.set_state(TaskCreation.description)


@manager_router.message(TaskCreation.description)
async def task_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process task description."""
    desc: str | None = None
    if message.text != "пропустить":
        desc = message.text
    await state.update_data(description=desc)
    async for session in get_session():
        performers = await get_users_by_role(session, UserRole.PERFORMER)
        if not performers:
            await message.answer("Нет исполнителей.")
            await state.clear()
            return
        text = _build_performers_text(performers)
        await message.answer(text)
        await state.set_state(TaskCreation.performer)


@manager_router.message(TaskCreation.performer)
async def task_performer(message: types.Message, state: FSMContext) -> None:
    """Process task performer."""
    try:
        performer_id = int(message.text)
    except ValueError:
        await message.answer("Введите числовой ID:")
        return
    await state.update_data(performer_id=performer_id)
    await message.answer(
        "Введите дедлайн (ДД.ММ.ГГГГ ЧЧ:ММ) "
        "или 'пропустить':",
    )
    await state.set_state(TaskCreation.deadline)


@manager_router.message(TaskCreation.deadline)
async def task_deadline(message: types.Message, state: FSMContext) -> None:
    """Process task deadline."""
    deadline = _parse_datetime(message.text, "%d.%m.%Y %H:%M")
    if deadline is None and message.text != "пропустить":
        await message.answer("Неверный формат:")
        return
    await state.update_data(deadline=deadline)
    await message.answer("Введите приоритет (1-5) или 'пропустить':")
    await state.set_state(TaskCreation.priority)


@manager_router.message(TaskCreation.priority)
async def task_priority(message: types.Message, state: FSMContext) -> None:
    """Process task priority and create task."""
    priority = 3
    if message.text != "пропустить":
        try:
            priority = int(message.text)
        except ValueError:
            await message.answer("Введите число 1-5:")
            return
    data = await state.get_data()
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        params = _build_task_params(data, user.id, priority)
        await create_task(session=session, params=params)
    await message.answer("Задача создана!")
    await state.clear()


@manager_router.callback_query(F.data.startswith("create_stage_"))
async def create_stage_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start stage creation."""
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text(
        "Создание этапа.\nВведите название:",
    )
    await state.set_state(StageCreation.title)


@manager_router.message(StageCreation.title)
async def stage_title(message: types.Message, state: FSMContext) -> None:
    """Process stage title."""
    await state.update_data(title=message.text)
    await message.answer("Введите описание (или 'пропустить'):")
    await state.set_state(StageCreation.description)


@manager_router.message(StageCreation.description)
async def stage_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage description."""
    desc: str | None = None
    if message.text != "пропустить":
        desc = message.text
    await state.update_data(description=desc)
    await message.answer("Введите порядок этапа (число):")
    await state.set_state(StageCreation.order)


@manager_router.message(StageCreation.order)
async def stage_order(message: types.Message, state: FSMContext) -> None:
    """Process stage order."""
    try:
        order = int(message.text)
    except ValueError:
        await message.answer("Введите число:")
        return
    await state.update_data(order=order)
    await message.answer(
        "Плановая дата начала (ДД.ММ.ГГГГ) "
        "или 'пропустить':",
    )
    await state.set_state(StageCreation.planned_start)


@manager_router.message(StageCreation.planned_start)
async def stage_start_date(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage start date."""
    start = _parse_datetime(message.text, "%d.%m.%Y")
    if start is None and message.text != "пропустить":
        await message.answer("Неверный формат:")
        return
    await state.update_data(planned_start=start)
    await message.answer(
        "Плановая дата окончания (ДД.ММ.ГГГГ) "
        "или 'пропустить':",
    )
    await state.set_state(StageCreation.planned_end)


@manager_router.message(StageCreation.planned_end)
async def stage_end_date(
    message: types.Message, state: FSMContext,
) -> None:
    """Process stage end date and create stage."""
    end = _parse_datetime(message.text, "%d.%m.%Y")
    if end is None and message.text != "пропустить":
        await message.answer("Неверный формат:")
        return
    data = await state.get_data()
    async for session in get_session():
        params = _build_stage_params(data)
        await create_stage(session=session, params=params)
    await message.answer("Этап создан!")
    await state.clear()


@manager_router.callback_query(F.data == "clients")
async def clients(callback: types.CallbackQuery) -> None:
    """Show clients list."""
    async for session in get_session():
        companies = await get_all_companies(session)
        await callback.message.edit_text(
            "Клиенты:", reply_markup=get_clients_keyboard(companies),
        )


@manager_router.callback_query(F.data == "add_client")
async def add_client_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start adding client."""
    await callback.message.edit_text(
        "Добавление клиента.\nНазвание компании:",
    )
    await state.set_state(CompanyCreation.name)


@manager_router.message(CompanyCreation.name)
async def company_name(message: types.Message, state: FSMContext) -> None:
    """Process company name."""
    await state.update_data(name=message.text)
    await message.answer("ИНН (или 'пропустить'):")
    await state.set_state(CompanyCreation.inn)


@manager_router.message(CompanyCreation.inn)
async def company_inn(message: types.Message, state: FSMContext) -> None:
    """Process company INN."""
    inn: str | None = None
    if message.text != "пропустить":
        inn = message.text
    await state.update_data(inn=inn)
    await message.answer("КПП (или 'пропустить'):")
    await state.set_state(CompanyCreation.kpp)


@manager_router.message(CompanyCreation.kpp)
async def company_kpp(message: types.Message, state: FSMContext) -> None:
    """Process company KPP."""
    kpp: str | None = None
    if message.text != "пропустить":
        kpp = message.text
    await state.update_data(kpp=kpp)
    await message.answer("Адрес (или 'пропустить'):")
    await state.set_state(CompanyCreation.address)


@manager_router.message(CompanyCreation.address)
async def company_address(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company address."""
    address: str | None = None
    if message.text != "пропустить":
        address = message.text
    await state.update_data(address=address)
    await message.answer("Телефон (или 'пропустить'):")
    await state.set_state(CompanyCreation.phone)


@manager_router.message(CompanyCreation.phone)
async def company_phone(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company phone."""
    phone: str | None = None
    if message.text != "пропустить":
        phone = message.text
    await state.update_data(phone=phone)
    await message.answer("Email (или 'пропустить'):")
    await state.set_state(CompanyCreation.email)


@manager_router.message(CompanyCreation.email)
async def company_email(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company email."""
    email: str | None = None
    if message.text != "пропустить":
        email = message.text
    await state.update_data(email=email)
    await message.answer("Сайт (или 'пропустить'):")
    await state.set_state(CompanyCreation.website)


@manager_router.message(CompanyCreation.website)
async def company_website(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company website and create company."""
    website: str | None = None
    if message.text != "пропустить":
        website = message.text
    await state.update_data(website=website)
    data = await state.get_data()
    async for session in get_session():
        params = _build_company_params(data)
        await create_company(session=session, params=params)
    await message.answer("Клиент добавлен!")
    await state.clear()


@manager_router.callback_query(F.data == "statistics")
async def statistics(callback: types.CallbackQuery) -> None:
    """Show statistics."""
    async for session in get_session():
        p_stats = await get_projects_count_by_status(session)
        t_stats = await get_tasks_count_by_status(session)
        u_stats = await get_users_count_by_role(session)
        text = _build_stats_text(p_stats, t_stats, u_stats)
        await callback.message.edit_text(
            text, reply_markup=get_back_keyboard(),
        )


@manager_router.callback_query(F.data == "all_tasks")
async def all_tasks(callback: types.CallbackQuery) -> None:
    """Show all tasks."""
    async for session in get_session():
        tasks = await get_tasks_by_project_id(session, 0)
        if not tasks:
            await callback.message.edit_text("Задач нет.")
            return
        await callback.message.edit_text(
            "Все задачи:", reply_markup=get_tasks_keyboard(tasks),
        )
