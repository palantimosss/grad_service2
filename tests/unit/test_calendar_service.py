"""Tests for calendar service."""

from datetime import UTC, datetime

import pytest

from bot.database.crud_modules.meeting_crud import create_meeting
from bot.services.calendar import (
    add_participant_service,
    cancel_meeting_service,
    complete_meeting_service,
    confirm_meeting_service,
    create_meeting_service,
)

# Test date constants
_TEST_YEAR = 2026
_TEST_MONTH = 12
_TEST_DAY = 31
_TEST_HOUR = 10

# Field key constants
_PROJECT_ID_KEY = "project_id"
_TITLE_KEY = "title"
_ORGANIZER_ID_KEY = "organizer_id"
_SCHEDULED_AT_KEY = "scheduled_at"

# Test data constant
_TEST_MEETING_TITLE = "Service Meeting"


@pytest.mark.asyncio
class TestCalendarService:
    """Tests for calendar service."""

    async def test_create_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating meeting through service."""
        meeting = await create_meeting_service(
            session=test_session,
            params={
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, 0, tzinfo=UTC,
                ),
            },
        )
        assert meeting is not None

    async def test_confirm_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test confirming meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, 0, tzinfo=UTC,
                ),
            },
        )
        confirmed = await confirm_meeting_service(test_session, meeting.id)
        assert confirmed is not None

    async def test_cancel_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test cancelling meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, 0, tzinfo=UTC,
                ),
            },
        )
        cancelled = await cancel_meeting_service(test_session, meeting.id)
        assert cancelled is not None

    async def test_complete_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test completing meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, 0, tzinfo=UTC,
                ),
            },
        )
        completed = await complete_meeting_service(test_session, meeting.id)
        assert completed is not None

    async def test_add_participant_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test adding participant through service."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, 0, tzinfo=UTC,
                ),
            },
        )
        participant = await add_participant_service(
            test_session,
            meeting.id,
            test_user.id,
        )
        assert participant is not None
