"""Document CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.enums import DocumentType

from bot.database.models.document import Document


class DocumentCreateParams(TypedDict, total=False):
    """Parameters for creating a document."""

    project_id: int
    task_id: int | None
    file_path: str
    file_name: str
    file_size: int
    document_type: DocumentType
    uploaded_by: int | None
    description: str | None


async def get_document_by_id(
    session: AsyncSession, document_id: int,
) -> Document | None:
    """Get document by ID."""
    query_result = await session.execute(
        select(Document).where(Document.id == document_id),
    )
    return query_result.scalar_one_or_none()


async def get_documents_by_project_id(
    session: AsyncSession, project_id: int,
) -> list[Document]:
    """Get documents by project ID."""
    query_result = await session.execute(
        select(Document).where(Document.project_id == project_id),
    )
    return list(query_result.scalars().all())


async def get_documents_by_task_id(
    session: AsyncSession, task_id: int,
) -> list[Document]:
    """Get documents by task ID."""
    query_result = await session.execute(
        select(Document).where(Document.task_id == task_id),
    )
    return list(query_result.scalars().all())


async def create_document(
    session: AsyncSession, document_data: DocumentCreateParams,
) -> Document:
    """Create a new document."""
    document = Document(**document_data)
    session.add(document)
    await session.commit()
    await session.refresh(document)
    return document


async def update_document(
    session: AsyncSession,
    document_id: int,
    document_data: DocumentCreateParams,
) -> Document | None:
    """Update document fields."""
    await session.execute(
        update(Document)
        .where(Document.id == document_id)
        .values(**document_data),
    )
    await session.commit()
    return await get_document_by_id(session, document_id)


async def delete_document(
    session: AsyncSession, document_id: int,
) -> bool:
    """Delete document by ID."""
    query_result = await session.execute(
        delete(Document).where(Document.id == document_id),
    )
    await session.commit()
    return query_result.rowcount > 0
