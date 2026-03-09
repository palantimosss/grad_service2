"""Files service module."""

import os
from typing import TYPE_CHECKING

from aiogram.types import FSInputFile

from bot.config import FILES_DIR
from bot.database.crud_modules.document_crud import (
    create_document as create_document_db,
)
from bot.database.crud_modules.document_crud import (
    delete_document as delete_document_db,
)
from bot.database.crud_modules.document_crud import (
    get_document_by_id as get_document_by_id_db,
)

if TYPE_CHECKING:
    from aiogram import Bot
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.document import Document
    from bot.database.models.enums import DocumentType


async def save_file(
    file_id: str,
    file_name: str,
    bot: Bot,
) -> str | None:
    """Save file from Telegram to local storage."""
    file = await bot.get_file(file_id)
    file_path = file.file_path

    dest_path = FILES_DIR / file_name
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    await bot.download_file(file_path, dest_path)

    return str(dest_path)


async def create_document_service(  # noqa: PLR0913
    session: AsyncSession,
    project_id: int,
    file_path: str,
    file_name: str,
    file_size: int,
    document_type: DocumentType,
    uploaded_by: int,
    task_id: int | None = None,
    description: str | None = None,
) -> Document | None:
    """Create document record in database."""
    return await create_document_db(
        session=session,
        params={
            "project_id": project_id,
            "file_path": file_path,
            "file_name": file_name,
            "file_size": file_size,
            "document_type": document_type,
            "uploaded_by": uploaded_by,
            "task_id": task_id,
            "description": description,
        },
    )


async def delete_document_service(
    session: AsyncSession,
    document_id: int,
) -> bool:
    """Delete document from database and filesystem."""
    doc = await get_document_by_id_db(session, document_id)
    if not doc:
        return False

    await _delete_file(doc.file_path)

    return await delete_document_db(session, document_id)


def _delete_file(file_path: str) -> None:
    """Delete file from filesystem."""
    if os.path.exists(file_path):  # noqa: PTH110
        os.remove(file_path)  # noqa: PTH107


def get_document_file(document_path: str) -> FSInputFile:
    """Get document as input file."""
    return FSInputFile(path=document_path)
