"""Performer document upload handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.document_crud import (
    DocumentCreateParams,
    create_document,
)
from bot.database.crud_modules.task_crud import get_task_by_id
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import DocumentType
from bot.keyboards.menus import get_back_keyboard
from bot.states.states import DocumentUpload

logger = logging.getLogger(__name__)

document_upload_router = Router()

_FILES_DIR = "data/files"
_PROJECT_ID_KEY = "project_id"
_TASK_ID_KEY = "task_id"


def _build_dest_path(project_id: int, file_name: str) -> str:
    """Build document destination path."""
    return f"{_FILES_DIR}/{project_id}_{file_name}"


async def _download_file(message: types.Message, dest: str) -> None:
    """Download document file from Telegram."""
    document_file = message.document
    file_path_obj = await message.bot.get_file(document_file.file_id)
    await message.bot.download_file(file_path_obj.file_path, dest)


async def _create_document_record(
    session: object,
    doc_data: dict,
) -> None:
    """Create document record in database."""
    doc_params: DocumentCreateParams = {
        _PROJECT_ID_KEY: doc_data[_PROJECT_ID_KEY],
        _TASK_ID_KEY: doc_data[_TASK_ID_KEY],
        "file_path": doc_data["file_path"],
        "file_name": doc_data["file_name"],
        "file_size": doc_data["file_size"],
        "document_type": DocumentType.WORK,
        "uploaded_by": doc_data["user_id"],
    }
    await create_document(session=session, params=doc_params)


async def _save_document(
    message: types.Message,
    task_id: int,
    project_id: int,
) -> None:
    """Save document file and create record."""
    document_file = message.document
    dest = _build_dest_path(project_id, document_file.file_name)
    await _download_file(message, dest)
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        doc_data = {
            _PROJECT_ID_KEY: project_id,
            _TASK_ID_KEY: task_id,
            "file_path": dest,
            "file_name": document_file.file_name,
            "file_size": document_file.file_size,
            "user_id": user.id,
        }
        await _create_document_record(session, doc_data)


@document_upload_router.callback_query(
    lambda callback: callback.data.startswith("upload_doc_task_"),
)
async def upload_doc_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start document upload for task."""
    parts = callback.data.split("_")
    task_id = int(parts[3])
    await state.update_data(task_id=task_id)
    async for session in get_session():
        task = await get_task_by_id(session, task_id)
        if task:
            await state.update_data(project_id=task.project_id)
    await callback.message.edit_text("Отправьте файл для загрузки:")
    await state.set_state(DocumentUpload.document_file)


@document_upload_router.message(DocumentUpload.document_file)
async def upload_doc_file(
    message: types.Message, state: FSMContext,
) -> None:
    """Process document file."""
    state_data = await state.get_data()
    task_id = state_data.get("task_id")
    project_id = state_data.get("project_id")
    if task_id and project_id:
        await _save_document(message, task_id, project_id)
        await message.answer(
            "Документ загружен!",
            reply_markup=get_back_keyboard(f"task_{task_id}"),
        )
    await state.clear()
