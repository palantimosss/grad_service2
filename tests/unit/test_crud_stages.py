"""Unit tests for stage CRUD operations."""

from datetime import UTC, datetime

import pytest

from bot.database.crud_modules.stage_crud import (
    create_stage,
    delete_stage,
    get_stage_by_id,
    get_stages_by_project_id,
    update_stage_status,
)

# Test date constants
_TEST_YEAR = 2026
_TEST_MONTH_START = 1
_TEST_DAY_START = 1
_TEST_MONTH_END = 2
_TEST_DAY_END = 1

# Test data constants
_TEST_STAGE_TITLE = "Design Phase"
_EXPECTED_STAGES_COUNT = 2

# Field keys
_PROJECT_ID_KEY = "project_id"
_TITLE_KEY = "title"
_ORDER_KEY = "order"
_PLANNED_START_KEY = "planned_start"
_PLANNED_END_KEY = "planned_end"
_STATUS_KEY = "status"


@pytest.mark.asyncio
class TestStageCRUD:
    """Tests for stage CRUD operations."""

    async def test_create_stage(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating stage."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_START, _TEST_DAY_START,
                    tzinfo=UTC,
                ),
                _PLANNED_END_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_END, _TEST_DAY_END,
                    tzinfo=UTC,
                ),
            },
        )
        assert stage.title == _TEST_STAGE_TITLE
        assert stage.order == 1

    async def test_get_stage_by_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting stage by ID."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_START, _TEST_DAY_START,
                    tzinfo=UTC,
                ),
                _PLANNED_END_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_END, _TEST_DAY_END,
                    tzinfo=UTC,
                ),
            },
        )
        retrieved = await get_stage_by_id(test_session, stage.id)
        assert retrieved is not None
        assert retrieved.title == _TEST_STAGE_TITLE

    async def test_get_stages_by_project_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting stages by project ID."""
        await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Stage 1",
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_START, _TEST_DAY_START,
                    tzinfo=UTC,
                ),
            },
        )
        await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Stage 2",
                _ORDER_KEY: 2,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_END, _TEST_DAY_END,
                    tzinfo=UTC,
                ),
            },
        )
        stages = await get_stages_by_project_id(
            test_session, test_project.id,
        )
        assert len(stages) == _EXPECTED_STAGES_COUNT

    async def test_update_stage_status(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test updating stage status."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH_START, _TEST_DAY_START,
                    tzinfo=UTC,
                ),
            },
        )
        updated = await update_stage_status(
            test_session, stage.id, "completed",
        )
        assert updated is not None
        assert updated.status == "completed"

    async def test_delete_stage(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test deleting stage."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
            },
        )
        deleted = await delete_stage(test_session, stage.id)
        assert deleted is True
        retrieved = await get_stage_by_id(test_session, stage.id)
        assert retrieved is None
