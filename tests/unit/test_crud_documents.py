"""Unit tests for document CRUD operations."""

import pytest

from bot.database.crud_modules.document_crud import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_project_id,
    update_document,
)
from bot.database.models.enums import DocumentType

# Test constants
_TEST_FILE_PATH = "/files/test.pdf"
_TEST_FILE_NAME = "test.pdf"
_TEST_FILE_SIZE = 1024
_EXPECTED_DOCS_COUNT = 2

# Field keys
_PROJECT_ID_KEY = "project_id"
_FILE_PATH_KEY = "file_path"
_FILE_NAME_KEY = "file_name"
_FILE_SIZE_KEY = "file_size"
_DOCUMENT_TYPE_KEY = "document_type"
_DESCRIPTION_KEY = "description"


@pytest.mark.asyncio
class TestDocumentCRUD:
    """Tests for document CRUD operations."""

    async def test_create_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating document."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: _TEST_FILE_NAME,
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        assert doc.file_name == _TEST_FILE_NAME
        assert doc.document_type == DocumentType.SOURCE

    async def test_get_document_by_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting document by ID."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: _TEST_FILE_NAME,
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        retrieved = await get_document_by_id(test_session, doc.id)
        assert retrieved is not None
        assert retrieved.file_name == _TEST_FILE_NAME

    async def test_get_documents_by_project_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting documents by project ID."""
        await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: "doc1.pdf",
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: "doc2.pdf",
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.WORK,
            },
        )
        docs = await get_documents_by_project_id(
            test_session, test_project.id,
        )
        assert len(docs) == _EXPECTED_DOCS_COUNT

    async def test_update_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test updating document."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: _TEST_FILE_NAME,
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        updated = await update_document(
            test_session,
            doc.id,
            {_FILE_NAME_KEY: "updated.pdf", _DESCRIPTION_KEY: "Updated doc"},
        )
        assert updated is not None
        assert updated.file_name == "updated.pdf"

    async def test_delete_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test deleting document."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: _TEST_FILE_PATH,
                _FILE_NAME_KEY: _TEST_FILE_NAME,
                _FILE_SIZE_KEY: _TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        deleted = await delete_document(test_session, doc.id)
        assert deleted is True
        retrieved = await get_document_by_id(test_session, doc.id)
        assert retrieved is None
