"""Tests for files service and stage service."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pytest

from bot.database.models.enums import DocumentType
from bot.services.files import (
    create_document_service,
    delete_document_service,
    get_document_file,
)
from bot.services.stage_service import create_stage_service

# Test date constants
_TEST_YEAR = 2026
_TEST_MONTH_START = 1
_TEST_DAY_START = 1
_TEST_MONTH_END = 2
_TEST_DAY_END = 1

# Field key constants
_PROJECT_ID_KEY = "project_id"
_TITLE_KEY = "title"
_ORDER_KEY = "order"
_PLANNED_START_KEY = "planned_start"
_PLANNED_END_KEY = "planned_end"

# Test data constant
_TEST_STAGE_TITLE = "Service Stage"


@pytest.mark.asyncio
class TestFilesService:
    """Tests for files service."""

    async def test_create_document_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating document through service."""
        doc = await create_document_service(
            session=test_session,
            document_data={
                "project_id": test_project.id,
                "file_path": "/files/test.pdf",
                "file_name": "test.pdf",
                "file_size": 1024,
                "document_type": DocumentType.SOURCE,
                "uploaded_by": test_user.id,
            },
        )
        assert doc is not None
        assert doc.file_name == "test.pdf"

    async def test_delete_document_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting document through service."""
        doc = await create_document_service(
            session=test_session,
            document_data={
                "project_id": test_project.id,
                "file_path": "/files/test_delete.pdf",
                "file_name": "test_delete.pdf",
                "file_size": 1024,
                "document_type": DocumentType.SOURCE,
                "uploaded_by": test_user.id,
            },
        )
        assert doc is not None

        with (
            patch("bot.services.files.os.path.exists", return_value=False),
            patch("bot.services.files.os.remove"),
        ):
            deleted = await delete_document_service(test_session, doc.id)
            assert deleted is True

    def test_get_document_file(self) -> None:
        """Test getting document file."""
        with patch("bot.services.files.FSInputFile") as mock_file:
            mock_file_instance = MagicMock()
            mock_file.return_value = mock_file_instance
            file_obj = get_document_file("/path/to/file.pdf")
            assert file_obj is not None


@pytest.mark.asyncio
class TestStageService:
    """Tests for stage service."""

    async def test_create_stage_service(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating stage through service."""
        stage = await create_stage_service(
            session=test_session,
            params={
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR,
                    _TEST_MONTH_START,
                    _TEST_DAY_START,
                    tzinfo=UTC,
                ),
                _PLANNED_END_KEY: datetime(
                    _TEST_YEAR,
                    _TEST_MONTH_END,
                    _TEST_DAY_END,
                    tzinfo=UTC,
                ),
            },
        )
        assert stage is not None
        assert stage.title == _TEST_STAGE_TITLE
