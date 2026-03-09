"""Client handlers: projects, documents, feedback."""

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

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
    create_project,
    get_project_by_id,
    get_projects_by_client_id,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import DocumentType, ProjectStatus
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
from bot.states.states import DocumentUpload, FeedbackCreation, ProjectCreation

logger = logging.getLogger(__name__)

client_router = Router()

_PROJECT_ID_KEY = "project_id"
_AUTHOR_ID_KEY = "author_id"
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


async def _create_document_in_db(
    session: object,
    doc_data: dict,
) -> None:
    """Create document in database."""
    doc_params: DocumentCreateParams = {
        _PROJECT_ID_KEY: doc_data[_PROJECT_ID_KEY],
        "file_path": doc_data["file_path"],
        "file_name": doc_data["file_name"],
        "file_size": doc_data["file_size"],
        "document_type": DocumentType.SOURCE,
        "uploaded_by": doc_data["user_id"],
    }
    await create_document(session=session, params=doc_params)


async def _create_feedback_in_db(
    session: object,
    feedback_data: dict,
) -> None:
    """Create feedback in database."""
    feedback_params: FeedbackCreateParams = {
        _PROJECT_ID_KEY: feedback_data[_PROJECT_ID_KEY],
        _AUTHOR_ID_KEY: feedback_data[_AUTHOR_ID_KEY],
        "message": feedback_data["message"],
        "rating": None,
    }
    await create_feedback(session=session, params=feedback_params)


@client_router.callback_query(
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


@client_router.callback_query(
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


@client_router.message(ProjectCreation.title)
async def project_title(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project title."""
    await state.update_data(title=message.text)
    await message.answer(f"Введите описание (или '{_SKIP_OPTION}'):")
    await state.set_state(ProjectCreation.description)


@client_router.message(ProjectCreation.description)
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


@client_router.message(ProjectCreation.deadline)
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


@client_router.message(ProjectCreation.budget)
async def project_budget(
    message: types.Message, state: FSMContext,
) -> None:
    """Process project budget and create project."""
    budget = parse_budget(message.text)
    if budget is None and message.text != _SKIP_OPTION:
        await message.answer("Введите число:")
        return
    await state.update_data(budget=budget)
    project_data = await state.get_data()
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await _create_project_in_db(session, project_data, user.id)
    await message.answer("Проект создан!")
    await state.clear()


@client_router.callback_query(
    lambda callback: callback.data.startswith("project_"),
)
async def project_detail(callback: types.CallbackQuery) -> None:
    """Show project details."""
    parts = callback.data.split("_")
    project_id = int(parts[1])
    async for session in get_session():
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


@client_router.callback_query(
    lambda callback: callback.data.startswith("upload_doc_"),
)
async def upload_doc_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start document upload."""
    parts = callback.data.split("_")
    project_id = int(parts[2])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Отправьте файл для загрузки:")
    await state.set_state(DocumentUpload.document_file)


@client_router.message(DocumentUpload.document_file)
async def upload_doc_file(
    message: types.Message, state: FSMContext,
) -> None:
    """Process document file."""
    state_data = await state.get_data()
    project_id = state_data.get("project_id")
    await _process_document_upload(message, state, project_id)


async def _process_document_upload(
    message: types.Message,
    state: FSMContext,
    project_id: int | None,
) -> None:
    """Process document upload and save to database."""
    document_file = message.document
    file_name = document_file.file_name
    file_size = document_file.file_size
    dest = f"data/files/{project_id}_{file_name}"
    file_path_obj = await message.bot.get_file(document_file.file_id)
    await message.bot.download_file(file_path_obj.file_path, dest)
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await _create_document_in_db(
            session,
            {
                "project_id": project_id,
                "file_path": dest,
                "file_name": file_name,
                "file_size": file_size,
                "user_id": user.id,
            },
        )
    await message.answer(
        "Документ загружен!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()


@client_router.callback_query(
    lambda callback: callback.data.startswith("feedback_"),
)
async def feedback_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start feedback creation."""
    parts = callback.data.split("_")
    project_id = int(parts[1])
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
    await _process_feedback_creation(message, state, project_id)


async def _process_feedback_creation(
    message: types.Message,
    state: FSMContext,
    project_id: int | None,
) -> None:
    """Process feedback creation and save to database."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await _create_feedback_in_db(
            session,
            {
                "project_id": project_id,
                "author_id": user.id,
                "message": message.text,
            },
        )
    await message.answer(
        "Спасибо за ваш отзыв!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()
