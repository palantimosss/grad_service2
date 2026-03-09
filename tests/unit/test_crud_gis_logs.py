"""Unit tests for GIS log CRUD operations."""

from datetime import UTC, datetime

import pytest

from bot.database.crud_modules.gis_log_crud import (
    create_gis_check_log,
    delete_gis_log,
    get_gis_logs_by_meeting_id,
)
from bot.database.crud_modules.meeting_crud import create_meeting

# Test date constants
_TEST_YEAR = 2026
_TEST_MONTH = 12
_TEST_DAY = 31
_TEST_HOUR = 10
_TEST_MINUTE = 0

# Test data constants
_TEST_MEETING_TITLE = "Test Meeting"
_TEST_ADDRESS = "Test Address"
_TEST_COORDINATES = "30.3158,59.9391"
_EXPECTED_LOGS_COUNT = 2

# Field keys
_MEETING_ID_KEY = "meeting_id"
_ADDRESS_KEY = "address"
_COORDINATES_KEY = "coordinates"
_INSIDE_ZONE_KEY = "inside_zone"


@pytest.mark.asyncio
class TestGISLogCRUD:
    """Tests for GIS log CRUD operations."""

    async def test_create_gis_check_log(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating GIS check log."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": _TEST_MEETING_TITLE,
                "organizer_id": test_user.id,
                "scheduled_at": datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        log = await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: _TEST_ADDRESS,
                _COORDINATES_KEY: _TEST_COORDINATES,
                _INSIDE_ZONE_KEY: True,
            },
        )
        assert log.address == _TEST_ADDRESS
        assert log.inside_zone is True

    async def test_get_gis_logs_by_meeting_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting GIS logs by meeting ID."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": _TEST_MEETING_TITLE,
                "organizer_id": test_user.id,
                "scheduled_at": datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: "Address 1",
                _COORDINATES_KEY: _TEST_COORDINATES,
                _INSIDE_ZONE_KEY: True,
            },
        )
        await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: "Address 2",
                _COORDINATES_KEY: _TEST_COORDINATES,
                _INSIDE_ZONE_KEY: False,
            },
        )
        logs = await get_gis_logs_by_meeting_id(
            test_session, meeting.id,
        )
        assert len(logs) == _EXPECTED_LOGS_COUNT

    async def test_delete_gis_log(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting GIS log."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": _TEST_MEETING_TITLE,
                "organizer_id": test_user.id,
                "scheduled_at": datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        log = await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: _TEST_ADDRESS,
                _COORDINATES_KEY: _TEST_COORDINATES,
                _INSIDE_ZONE_KEY: True,
            },
        )
        deleted = await delete_gis_log(test_session, log.id)
        assert deleted is True
        logs = await get_gis_logs_by_meeting_id(test_session, meeting.id)
        assert len(logs) == 0
