"""Tests for database module and notification CRUD."""

import pytest
from sqlalchemy import select

from bot.database.crud_modules.notification_crud import (
    create_notification,
    delete_notification,
    get_notification_by_id,
    get_notifications_by_user_id,
    get_unread_notifications,
    mark_all_notifications_as_read,
    mark_notification_as_read,
)
from bot.database.database import (
    create_tables,
    get_session,
)
from bot.database.models.enums import NotificationType
from bot.database.models.notification import Notification

# Constants for test assertions
EXPECTED_TWO_ITEMS = 2

# Field key constants
_USER_ID_KEY = "user_id"
_TITLE_KEY = "title"
_MESSAGE_KEY = "message"
_NOTIFICATION_TYPE_KEY = "notification_type"

# Test data constants
TEST_NOTIFICATION_TITLE = "Test Notification"
TEST_NOTIFICATION_MESSAGE = "Test message"


@pytest.mark.asyncio
class TestNotificationCRUD:
    """Tests for notification CRUD operations."""

    async def test_create_notification(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test creating notification."""
        notification = await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: TEST_NOTIFICATION_TITLE,
                _MESSAGE_KEY: TEST_NOTIFICATION_MESSAGE,
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        assert notification.title == TEST_NOTIFICATION_TITLE
        assert notification.is_read is False

    async def test_get_notification_by_id(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting notification by ID."""
        notification = await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: TEST_NOTIFICATION_TITLE,
                _MESSAGE_KEY: TEST_NOTIFICATION_MESSAGE,
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        retrieved = await get_notification_by_id(test_session, notification.id)
        assert retrieved is not None
        assert retrieved.title == TEST_NOTIFICATION_TITLE

    async def test_get_notifications_by_user_id(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting notifications by user ID."""
        await create_notification(
            test_session,
            {
                "user_id": test_user.id,
                "title": "Notification 1",
                "message": "Message 1",
                "notification_type": NotificationType.NEW_TASK,
            },
        )
        await create_notification(
            test_session,
            {
                "user_id": test_user.id,
                "title": "Notification 2",
                "message": "Message 2",
                "notification_type": NotificationType.DEADLINE_SOON,
            },
        )
        notifications = await get_notifications_by_user_id(
            test_session, test_user.id,
        )
        assert len(notifications) == EXPECTED_TWO_ITEMS

    async def test_mark_notification_as_read(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test marking notification as read."""
        notification = await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: TEST_NOTIFICATION_TITLE,
                _MESSAGE_KEY: TEST_NOTIFICATION_MESSAGE,
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        assert notification.is_read is False

        updated = await mark_notification_as_read(
            test_session, notification.id,
        )
        assert updated is not None
        assert updated.is_read is True

    async def test_delete_notification(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test deleting notification."""
        notification = await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: TEST_NOTIFICATION_TITLE,
                _MESSAGE_KEY: TEST_NOTIFICATION_MESSAGE,
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        deleted = await delete_notification(test_session, notification.id)
        assert deleted is True
        retrieved = await get_notification_by_id(test_session, notification.id)
        assert retrieved is None

    async def test_get_unread_notifications_count(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting unread notifications count."""
        await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: "Unread Notification",
                _MESSAGE_KEY: "Message",
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: "Read Notification",
                _MESSAGE_KEY: "Message",
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        # Mark second as read
        query_result = await test_session.execute(
            select(Notification)
            .where(Notification.title == "Read Notification"),
        )
        notification_item = query_result.scalar_one()
        notification_item.is_read = True
        await test_session.commit()

        unread = await get_unread_notifications(test_session, test_user.id)
        assert len(unread) == 1

    async def test_mark_all_notifications_as_read(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test marking all notifications as read."""
        await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: "Notification 1",
                _MESSAGE_KEY: "Message 1",
                _NOTIFICATION_TYPE_KEY: NotificationType.NEW_TASK,
            },
        )
        await create_notification(
            test_session,
            {
                _USER_ID_KEY: test_user.id,
                _TITLE_KEY: "Notification 2",
                _MESSAGE_KEY: "Message 2",
                _NOTIFICATION_TYPE_KEY: NotificationType.DEADLINE_SOON,
            },
        )
        await mark_all_notifications_as_read(test_session, test_user.id)

        notifications = await get_notifications_by_user_id(
            test_session, test_user.id,
        )
        assert all(notification.is_read for notification in notifications)


class TestDatabase:
    """Tests for database module."""

    def test_get_session(self) -> None:
        """Test get_session function."""
        # Just test it returns an async generator
        assert get_session is not None

    async def test_create_tables(self) -> None:
        """Test create_tables function."""
        # Should not raise
        await create_tables()
