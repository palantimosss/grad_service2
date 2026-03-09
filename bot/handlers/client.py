"""Client handlers: projects, documents, feedback."""

import logging
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from aiogram import F, Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.document_crud import (
    DocumentCreateParams,
    create_document,
)
from bot.database.crud_modules.feedback_crud import (
    FeedbackCreateParams,
    create_feedback,
)
from bot.database.crud_modules.project_crud import (
    ProjectCreateParams,
    create_project,
    get_project_by_id,
    get_projects_by_client_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import DocumentType, ProjectStatus
from bot.keyboards.menus import (
    get_back_keyboard,
    get_project_actions_keyboard,
    get_projects_keyboard,
)
from bot.states.states import DocumentUpload, FeedbackCreation, ProjectCreation

logger = logging.getLogger(__name__)

client_router = Router()

# Status map for display
_STATUS_MAP = {
    "draft": "Черновик",
    "pending": "На регистрации",
    "registered": "Зарегистрирован",
    "in_progress": "В работе",
    "on_hold": "Приостановлен",
    "completed": "Завершён",
    "archived": "Архив",
}

# Skip option text
_SKIP_OPTION = "пропустить"


def _parse_deadline(text: str) -> datetime | None:
    """Parse deadline from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return datetime.strptime(text, "%d.%m.%Y %H:%M").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def _parse_budget(text: str) -> float | None:
    """Parse budget from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def _build_project_params(
    project_data: dict,
    user_id: int,
) -> ProjectCreateParams:
    """Build project creation params."""
    params: ProjectCreateParams = {
        "title": project_data["title"],
        "client_id": user_id,
        "status": ProjectStatus.PENDING,
    }
    if project_data.get("description"):
        params["description"] = project_data["description"]
    if project_data.get("deadline"):
        params["deadline"] = project_data["deadline"]
    if project_data.get("budget") is not None:
        params["budget"] = project_data["budget"]
    return params


@client_router.callback_query(F.data == "my_projects")
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


@client_router.callback_query(F.data == "create_project")
async def create_project_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start project creation."""
    await callback.message.edit_text(
        "Создание нового проекта.\nВведите название проекта:",
    )
    await state.set_state(ProjectCreation.title)


@client_router.message(ProjectCreation.title)
async def project_title(message: types.Message, state: FSMContext) -> None:
    """Process project title."""
    await state.update_data(title=message.text)
    await message.answer(
        f"Введите описание проекта (или '{_SKIP_OPTION}'):",
    )
    await state.set_state(ProjectCreation.description)


@client_router.message(ProjectCreation.description)
async def project_description(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project description."""
    desc: str | None = None
    if message.text != _SKIP_OPTION:
        desc = message.text
    await state.update_data(description=desc)
    await message.answer(
        "Введите дедлайн в формате ДД.ММ.ГГГГ ЧЧ:ММ "
        f"(или '{_SKIP_OPTION}'):",
    )
    await state.set_state(ProjectCreation.deadline)


@client_router.message(ProjectCreation.deadline)
async def project_deadline(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project deadline."""
    deadline = _parse_deadline(message.text)
    if deadline is None and message.text != _SKIP_OPTION:
        await message.answer(
            "Неверный формат. Попробуйте снова или "
            f"'{_SKIP_OPTION}':",
        )
        return
    await state.update_data(deadline=deadline)
    await message.answer(f"Введите бюджет (или '{_SKIP_OPTION}'):")
    await state.set_state(ProjectCreation.budget)


@client_router.message(ProjectCreation.budget)
async def project_budget(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project budget."""
    budget = _parse_budget(message.text)
    if budget is None and message.text != _SKIP_OPTION:
        await message.answer(
            "Неверный формат. Попробуйте снова или "
            f"'{_SKIP_OPTION}':",
        )
        return
    await state.update_data(budget=budget)
    project_data = await state.get_data()
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        params = _build_project_params(project_data, user.id)
        await create_project(session=session, params=params)
    await message.answer(
        "Проект создан и отправлен на регистрацию!",
        reply_markup=get_back_keyboard("my_projects"),
    )
    await state.clear()


@client_router.callback_query(F.data.startswith("project_"))
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    project_id = int(callback.data.split("_")[1])
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        project = await get_project_by_id(session, project_id)
        if not project:
            await callback.answer("Проект не найден", show_alert=True)
            return
        status_text = _STATUS_MAP.get(
            project.status.value, project.status.value,
        )
        status_label = "Статус"
        desc_label = "Описание"
        deadline_label = "Дедлайн"
        budget_label = "Бюджет"
        lines = [
            f"<b>{project.title}</b>",
            "",
            f"{status_label}: {status_text}",
            f"{desc_label}: {project.description or 'Нет'}",
            f"{deadline_label}: {project.deadline or 'Не установлен'}",
            f"{budget_label}: {project.budget or 'Не указан'}",
        ]
        text = "\n".join(lines)
        await callback.message.edit_text(
            text,
            reply_markup=get_project_actions_keyboard(project_id, user.role),
        )


@client_router.callback_query(F.data.startswith("upload_doc_"))
async def upload_doc_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start document upload."""
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Отправьте файл для загрузки:")
    await state.set_state(DocumentUpload.document_file)


@client_router.message(DocumentUpload.document_file, F.document)
async def upload_doc_file(
    message: types.Message, state: FSMContext,
) -> None:
    """Process document file."""
    state_data = await state.get_data()
    project_id = state_data.get("project_id")
    document_file = message.document
    file_name = document_file.file_name
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        file_path_obj = await message.bot.get_file(document_file.file_id)
        dest = f"data/files/{project_id}_{file_name}"
        await message.bot.download_file(file_path_obj.file_path, dest)
        params: DocumentCreateParams = {
            "project_id": project_id,
            "file_path": dest,
            "file_name": file_name,
            "file_size": document_file.file_size,
            "document_type": DocumentType.SOURCE,
            "uploaded_by": user.id,
        }
        await create_document(session=session, params=params)
    await message.answer(
        "Документ загружен!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()


@client_router.callback_query(F.data.startswith("feedback_"))
async def feedback_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start feedback creation."""
    project_id = int(callback.data.split("_")[1])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Введите ваш отзыв о проекте:")
    await state.set_state(FeedbackCreation.message)


@client_router.message(FeedbackCreation.message)
async def feedback_message(
    message: types.Message, state: FSMContext,
) -> None:
    """Process feedback message."""
    state_data = await state.get_data()
    project_id = state_data.get("project_id")
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        params: FeedbackCreateParams = {
            "project_id": project_id,
            "author_id": user.id,
            "message": message.text,
            "rating": None,
        }
        await create_feedback(session=session, params=params)
    await message.answer(
        "Спасибо за ваш отзыв!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()
