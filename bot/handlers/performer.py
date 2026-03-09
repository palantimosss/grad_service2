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

STATUS_MAP = {
    "pending": "Ожидает",
    "in_progress": "В работе",
    "review": "На проверке",
    "completed": "Завершена",
    "cancelled": "Отменена",
}


def _build_task_text(task: object, status_text: str) -> str:
    """Build task detail text."""
    desc = task.description or "Нет"
    deadline = task.deadline or "Не установлен"
    lines = [
        f"<b>{task.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Описание: {desc}",
        f"Приоритет: {task.priority}",
        f"Дедлайн: {deadline}",
    ]
    return "\n".join(lines)


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
    data = callback.data
    if data.startswith("task_start_"):
        await _start_task(callback)
        return
    if data.startswith("task_complete_"):
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
        status_text = STATUS_MAP.get(task.status.value, task.status.value)
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
    await state.set_state(DocumentUpload.file)


@performer_router.message(DocumentUpload.file, F.document)
async def upload_doc_file(
    message: types.Message, state: FSMContext,
) -> None:
    """Process document file."""
    data = await state.get_data()
    task_id = data.get("task_id")
    project_id = data.get("project_id")
    file = message.document
    file_name = file.file_name
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        file_path_obj = await message.bot.get_file(file.file_id)
        dest = f"data/files/{project_id}_{file_name}"
        await message.bot.download_file(file_path_obj.file_path, dest)
        params: DocumentCreateParams = {
            "project_id": project_id,
            "task_id": task_id,
            "file_path": dest,
            "file_name": file_name,
            "file_size": file.file_size,
            "document_type": DocumentType.WORK,
            "uploaded_by": user.id,
        }
        await create_document(session=session, params=params)
    await message.answer(
        "Документ загружен!",
        reply_markup=get_back_keyboard(f"task_{task_id}"),
    )
    await state.clear()


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
