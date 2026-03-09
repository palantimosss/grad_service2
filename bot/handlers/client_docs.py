"""Client handlers: documents."""

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.document_crud import (
    DocumentCreateParams,
    create_document,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.database.models.enums import DocumentType
from bot.keyboards.menus import get_back_keyboard
from bot.states.states import DocumentUpload

logger = logging.getLogger(__name__)

client_docs_router = Router()

_PROJECT_ID_KEY = "project_id"


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


@client_docs_router.callback_query(
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


@client_docs_router.message(DocumentUpload.document_file)
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
    dest = await _download_document(message, project_id)
    async for session in get_session():
        await _save_document_to_db(session, message, project_id, dest)
    await _send_upload_complete(message, state, project_id)


async def _download_document(
    message: types.Message,
    project_id: int | None,
) -> str:
    """Download document and return destination path."""
    document_file = message.document
    file_name = document_file.file_name
    dest = f"data/files/{project_id}_{file_name}"
    file_path_obj = await message.bot.get_file(document_file.file_id)
    await message.bot.download_file(file_path_obj.file_path, dest)
    return dest


async def _save_document_to_db(
    session: object,
    message: types.Message,
    project_id: int | None,
    dest: str,
) -> None:
    """Save document info to database."""
    user = await get_user_by_telegram_id(session, message.from_user.id)
    document_file = message.document
    await _create_document_in_db(
        session,
        {
            "project_id": project_id,
            "file_path": dest,
            "file_name": document_file.file_name,
            "file_size": document_file.file_size,
            "user_id": user.id,
        },
    )


async def _send_upload_complete(
    message: types.Message,
    state: FSMContext,
    project_id: int | None,
) -> None:
    """Send upload complete message and clear state."""
    await message.answer(
        "Документ загружен!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()
