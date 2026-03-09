"""Performer handlers: tasks, documents."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.document_crud import (
    DocumentCreateParams,
    create_document,
)
from bot.database.crud_modules.project_crud import (
    get_projects_by_manager_id,
)
from bot.database.crud_modules.task_crud import (
    get_task_by_id,
    get_tasks_by_performer_id,
    update_task_status,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import DocumentType, TaskStatus
from bot.keyboards.menus import (
    get_back_keyboard,
    get_projects_keyboard,
    get_task_actions_keyboard,
    get_tasks_keyboard,
)
from bot.states.states import DocumentUpload

logger = logging.getLogger(__name__)

performer_router = Router()

# Status map for display (immutable tuple)
_STATUS_MAP = (
    ("pending", "Ожидает"),
    ("in_progress", "В работе"),
    ("review", "На проверке"),
    ("completed", "Завершена"),
    ("cancelled", "Отменена"),
)


def _get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, value in _STATUS_MAP:
        if key == status_value:
            return value
    return status_value


def _build_task_text(task: object, status_text: str) -> str:
    """Build task detail text."""
    desc_val = task.description or "Нет"
    deadline_val = task.deadline or "Не установлен"
    priority_val = task.priority
    return "\n".join([
        f"<b>{task.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Описание: {desc_val}",
        f"Приоритет: {priority_val}",
        f"Дедлайн: {deadline_val}",
    ])


@performer_router.callback_query(F.data == "my_tasks")
async def my_tasks(callback: types.CallbackQuery) -> None:
    """Show performer's tasks."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(
                "Сначала зарегистрируйтесь", show_alert=True,
            )
            return
        tasks = await get_tasks_by_performer_id(session, user.id)
        if not tasks:
            await callback.message.edit_text("У вас нет задач.")
            return
        await callback.message.edit_text(
            "Ваши задачи:", reply_markup=get_tasks_keyboard(tasks),
        )


@performer_router.callback_query(F.data.startswith("task_"))
async def task_detail(callback: types.CallbackQuery) -> None:
    """Show task details."""
    callback_data = callback.data
    if callback_data.startswith("task_start_"):
        await _start_task(callback)
        return
    if callback_data.startswith("task_complete_"):
        await _complete_task(callback)
        return
    await _show_task_info(callback)


async def _start_task(callback: types.CallbackQuery) -> None:
    """Start task."""
    task_id = int(callback.data.split("_")[2])
    async for session in get_session():
        await update_task_status(
            session, task_id, TaskStatus.IN_PROGRESS,
        )
    await callback.message.edit_text(f"Задача {task_id} взята в работу.")


async def _complete_task(callback: types.CallbackQuery) -> None:
    """Complete task."""
    task_id = int(callback.data.split("_")[2])
    async for session in get_session():
        await update_task_status(
            session, task_id, TaskStatus.COMPLETED,
        )
    await callback.message.edit_text("Задача завершена!")


async def _show_task_info(callback: types.CallbackQuery) -> None:
    """Show task information."""
    task_id = int(callback.data.split("_")[1])
    async for session in get_session():
        task = await get_task_by_id(session, task_id)
        if not task:
            await callback.answer("Задача не найдена", show_alert=True)
            return
        status_text = _get_status_text(task.status.value)
        text = _build_task_text(task, status_text)
        await callback.message.edit_text(
            text,
            reply_markup=get_task_actions_keyboard(task_id, task.status),
        )


@performer_router.callback_query(F.data.startswith("upload_doc_task_"))
async def upload_doc_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start document upload for task."""
    task_id = int(callback.data.split("_")[3])
    await state.update_data(task_id=task_id)
    async for session in get_session():
        task = await get_task_by_id(session, task_id)
        if task:
            await state.update_data(project_id=task.project_id)
    await callback.message.edit_text("Отправьте файл для загрузки:")
    await state.set_state(DocumentUpload.document_file)


@performer_router.message(DocumentUpload.document_file, F.document)
async def upload_doc_file(
    message: types.Message, state: FSMContext,
) -> None:
    """Process document file."""
    state_data = await state.get_data()
    task_id = state_data.get("task_id")
    project_id = state_data.get("project_id")
    await _save_and_create_document(message, task_id, project_id)
    await message.answer(
        "Документ загружен!",
        reply_markup=get_back_keyboard(f"task_{task_id}"),
    )
    await state.clear()


async def _save_and_create_document(
    message: types.Message, task_id: int, project_id: int,
) -> None:
    """Save document file and create document record."""
    document_file = message.document
    file_name = document_file.file_name
    dest = f"data/files/{project_id}_{file_name}"
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        file_path_obj = await message.bot.get_file(document_file.file_id)
        await message.bot.download_file(file_path_obj.file_path, dest)
        doc_params: DocumentCreateParams = {
            "project_id": project_id,
            "task_id": task_id,
            "file_path": dest,
            "file_name": file_name,
            "file_size": document_file.file_size,
            "document_type": DocumentType.WORK,
            "uploaded_by": user.id,
        }
        await create_document(session=session, params=doc_params)


@performer_router.callback_query(F.data == "projects")
async def projects(callback: types.CallbackQuery) -> None:
    """Show projects for performer."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(
                "Сначала зарегистрируйтесь", show_alert=True,
            )
            return
        projects = await get_projects_by_manager_id(session, user.id)
        if not projects:
            await callback.message.edit_text("У вас нет проектов.")
            return
        await callback.message.edit_text(
            "Ваши проекты:",
            reply_markup=get_projects_keyboard(projects),
        )
