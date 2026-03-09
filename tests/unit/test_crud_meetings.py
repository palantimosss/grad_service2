"""Unit tests for meeting CRUD operations."""

from datetime import UTC, datetime

import pytest

from bot.database.crud_modules.meeting_crud import (
    add_meeting_participant,
    create_meeting,
    delete_meeting,
    get_meeting_by_id,
    get_meetings_by_project_id,
    update_meeting_status,
    update_participant_status,
)
from bot.database.models.enums import MeetingParticipantStatus, MeetingStatus

# Test date constants
_TEST_YEAR = 2026
_TEST_MONTH = 12
_TEST_DAY = 31
_TEST_HOUR = 10
_TEST_MINUTE = 0

# Test data constants
_TEST_MEETING_TITLE = "Test Meeting"
_EXPECTED_MEETINGS_COUNT = 2

# Field keys
_PROJECT_ID_KEY = "project_id"
_TITLE_KEY = "title"
_ORGANIZER_ID_KEY = "organizer_id"
_SCHEDULED_AT_KEY = "scheduled_at"
_DURATION_MINUTES_KEY = "duration_minutes"
_IS_ONLINE_KEY = "is_online"


@pytest.mark.asyncio
class TestMeetingCRUD:
    """Tests for meeting CRUD operations."""

    async def test_create_meeting(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating meeting."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
                _DURATION_MINUTES_KEY: 60,
                _IS_ONLINE_KEY: True,
            },
        )
        assert meeting.title == _TEST_MEETING_TITLE
        assert meeting.is_online is True

    async def test_get_meeting_by_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting meeting by ID."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        retrieved = await get_meeting_by_id(test_session, meeting.id)
        assert retrieved is not None
        assert retrieved.title == _TEST_MEETING_TITLE

    async def test_get_meetings_by_project_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting meetings by project ID."""
        await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Meeting 1",
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Meeting 2",
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR + 1, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        meetings = await get_meetings_by_project_id(
            test_session, test_project.id,
        )
        assert len(meetings) == _EXPECTED_MEETINGS_COUNT

    async def test_update_meeting_status(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test updating meeting status."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        updated = await update_meeting_status(
            test_session, meeting.id, MeetingStatus.CONFIRMED,
        )
        assert updated is not None
        assert updated.status == MeetingStatus.CONFIRMED

    async def test_delete_meeting(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting meeting."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        deleted = await delete_meeting(test_session, meeting.id)
        assert deleted is True
        retrieved = await get_meeting_by_id(test_session, meeting.id)
        assert retrieved is None

    async def test_add_meeting_participant(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test adding meeting participant."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        participant = await add_meeting_participant(
            test_session,
            meeting.id,
            test_user.id,
        )
        assert participant.meeting_id == meeting.id
        assert participant.user_id == test_user.id
        assert participant.status == MeetingParticipantStatus.PENDING

    async def test_update_participant_status(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test updating participant status."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: _TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    _TEST_YEAR, _TEST_MONTH, _TEST_DAY,
                    _TEST_HOUR, _TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        await add_meeting_participant(
            test_session,
            meeting.id,
            test_user.id,
        )
        participant = await update_participant_status(
            test_session,
            meeting.id,
            test_user.id,
            MeetingParticipantStatus.CONFIRMED,
        )
        assert participant is not None
        assert participant.status == MeetingParticipantStatus.CONFIRMED
