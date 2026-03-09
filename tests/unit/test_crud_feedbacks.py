"""Unit tests for feedback CRUD operations."""

import pytest

from bot.database.crud_modules.feedback_crud import (
    create_feedback,
    delete_feedback,
    get_feedback_by_id,
    get_feedbacks_by_project_id,
)

# Test constants
_TEST_FEEDBACK_MESSAGE = "Great project!"
_TEST_RATING = 5
_EXPECTED_FEEDBACKS_COUNT = 2

# Field keys
_PROJECT_ID_KEY = "project_id"
_AUTHOR_ID_KEY = "author_id"
_MESSAGE_KEY = "message"
_RATING_KEY = "rating"


@pytest.mark.asyncio
class TestFeedbackCRUD:
    """Tests for feedback CRUD operations."""

    async def test_create_feedback(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating feedback."""
        feedback = await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: _TEST_FEEDBACK_MESSAGE,
                _RATING_KEY: _TEST_RATING,
            },
        )
        assert feedback.message == _TEST_FEEDBACK_MESSAGE
        assert feedback.rating == _TEST_RATING

    async def test_get_feedback_by_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting feedback by ID."""
        feedback = await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: _TEST_FEEDBACK_MESSAGE,
                _RATING_KEY: _TEST_RATING,
            },
        )
        retrieved = await get_feedback_by_id(test_session, feedback.id)
        assert retrieved is not None
        assert retrieved.message == _TEST_FEEDBACK_MESSAGE

    async def test_get_feedbacks_by_project_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting feedbacks by project ID."""
        await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: "Feedback 1",
                _RATING_KEY: 4,
            },
        )
        await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: "Feedback 2",
                _RATING_KEY: _TEST_RATING,
            },
        )
        feedbacks = await get_feedbacks_by_project_id(
            test_session, test_project.id,
        )
        assert len(feedbacks) == _EXPECTED_FEEDBACKS_COUNT

    async def test_delete_feedback(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting feedback."""
        feedback = await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: _TEST_FEEDBACK_MESSAGE,
                _RATING_KEY: _TEST_RATING,
            },
        )
        deleted = await delete_feedback(test_session, feedback.id)
        assert deleted is True
        retrieved = await get_feedback_by_id(test_session, feedback.id)
        assert retrieved is None
