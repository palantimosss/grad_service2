"""Document keyboards: documents list, document download, document type."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.enums import DocumentType

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

from bot.keyboards._common import (
    _BACK_DOCUMENTS,
    _BACK_TEXT,
    _adjust_double,
    _adjust_single,
    _build_double_column_keyboard,
)


def get_documents_keyboard(
    documents: list, project_id: int, task_id: int | None = None,
) -> InlineKeyboardMarkup:
    """Get documents list keyboard."""
    builder = InlineKeyboardBuilder()
    for doc in documents:
        builder.button(
            text=f"📄 {doc.file_name}",
            callback_data=f"doc_{doc.id}",
        )
    back_callback = f"task_{task_id}" if task_id else f"project_{project_id}"
    builder.button(text=_BACK_TEXT, callback_data=back_callback)
    _adjust_single(builder)
    return builder.as_markup()


def get_document_download_keyboard(
    document_id: int,
    can_delete: bool = False,  # noqa: FBT001, FBT002
) -> InlineKeyboardMarkup:
    """Get document download keyboard."""
    buttons = [("Скачать", f"download_doc_{document_id}")]
    if can_delete:
        buttons.append(("Удалить", f"delete_doc_{document_id}"))
    buttons.append((_BACK_TEXT, _BACK_DOCUMENTS))
    return _build_double_column_keyboard(buttons)


def get_document_type_keyboard() -> InlineKeyboardMarkup:
    """Get document type selection keyboard."""
    builder = InlineKeyboardBuilder()
    for doc_type in DocumentType:
        builder.button(
            text=doc_type.value.replace("_", " ").title(),
            callback_data=f"doc_type_{doc_type.value}",
        )
    _adjust_double(builder)
    return builder.as_markup()
