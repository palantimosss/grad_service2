"""Integration tests for services."""

from datetime import UTC, datetime

import pytest

from bot.database.models.enums import NotificationType, TaskStatus
from bot.services.notification import send_notification
from bot.services.project import create_project_service
from bot.services.task_service import create_task_service

# Test date constants
TEST_PROJECT_DEADLINE_YEAR = 2026
TEST_PROJECT_DEADLINE_MONTH = 12
TEST_PROJECT_DEADLINE_DAY = 31
TEST_TASK_DEADLINE_YEAR = 2026
TEST_TASK_DEADLINE_MONTH = 6
TEST_TASK_DEADLINE_DAY = 30

TASK_PRIORITY = 5


@pytest.mark.asyncio
class TestProjectService:
    """Tests for project service."""

    async def test_create_project_service(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test project creation through service."""
        project = await create_project_service(
            session=test_session,
            params={
                "client_id": test_user.id,  # type: ignore[union-attr]
                "title": "Service Test Project",
                "description": "Test",
                "deadline": datetime(
                    TEST_PROJECT_DEADLINE_YEAR,
                    TEST_PROJECT_DEADLINE_MONTH,
                    TEST_PROJECT_DEADLINE_DAY,
                    tzinfo=UTC,
                ),
                "budget": 100000.0,
            },
        )

        assert project is not None
        title = project.title  # type: ignore[union-attr]
        assert title == "Service Test Project"


@pytest.mark.asyncio
class TestTaskService:
    """Tests for task service."""

    async def test_create_task_service(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test task creation through service."""
        task = await create_task_service(
            session=test_session,
            params={
                "project_id": test_project.id,  # type: ignore[union-attr]
                "title": "Service Test Task",
                "description": "Test",
                "performer_id": None,
                "manager_id": None,
                "deadline": datetime(
                    TEST_TASK_DEADLINE_YEAR,
                    TEST_TASK_DEADLINE_MONTH,
                    TEST_TASK_DEADLINE_DAY,
                    tzinfo=UTC,
                ),
                "priority": TASK_PRIORITY,
                "status": TaskStatus.PENDING,
            },
        )

        assert task is not None
        title = task.title  # type: ignore[union-attr]
        assert title == "Service Test Task"
        priority = task.priority  # type: ignore[union-attr]
        assert priority == TASK_PRIORITY


@pytest.mark.asyncio
class TestNotificationService:
    """Tests for notification service."""

    async def test_send_notification(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test sending notification."""
        notification = await send_notification(
            session=test_session,
            params={
                "user_id": test_user.id,  # type: ignore[union-attr]
                "title": "Test Notification",
                "message": "Test message",
                "notification_type": NotificationType.NEW_TASK,
            },
        )

        assert notification is not None
        title = notification.title  # type: ignore[union-attr]
        assert title == "Test Notification"
