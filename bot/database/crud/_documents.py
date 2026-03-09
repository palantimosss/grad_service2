"""Document CRUD operations."""

from bot.database.crud_modules.document_crud import (
    DocumentCreateParams,
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_project_id,
    get_documents_by_task_id,
    update_document,
)

__all__ = [
    "DocumentCreateParams",
    "create_document",
    "delete_document",
    "get_document_by_id",
    "get_documents_by_project_id",
    "get_documents_by_task_id",
    "update_document",
]
