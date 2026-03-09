"""Unit tests for database models."""

import pytest

from bot.database.models.enums import (
    DocumentType,
    ProjectStatus,
    TaskStatus,
    UserRole,
)

TEST_TELEGRAM_ID = 123456789
TASK_PRIORITY_DEFAULT = 3


class TestUserModel:
    """Tests for User model."""

    @pytest.mark.asyncio
    async def test_create_user(
        self,
        test_user: object,
    ) -> None:
        """Test user creation."""
        tid = test_user.telegram_id  # type: ignore[union-attr]
        assert tid == TEST_TELEGRAM_ID
        assert test_user.role == UserRole.CLIENT  # type: ignore[union-attr]

    @pytest.mark.asyncio
    async def test_user_to_dict(self, test_user: object) -> None:
        """Test user to_dict method."""
        user_dict = test_user.to_dict()  # type: ignore[union-attr]
        assert "telegram_id" in user_dict
        assert user_dict["telegram_id"] == TEST_TELEGRAM_ID


class TestProjectModel:
    """Tests for Project model."""

    @pytest.mark.asyncio
    async def test_create_project(
        self,
        test_project: object,
    ) -> None:
        """Test project creation."""
        title = test_project.title  # type: ignore[union-attr]
        assert title == "Test Project"
        status = test_project.status  # type: ignore[union-attr]
        assert status == ProjectStatus.DRAFT

    @pytest.mark.asyncio
    async def test_project_to_dict(
        self,
        test_project: object,
    ) -> None:
        """Test project to_dict method."""
        project_dict = test_project.to_dict()  # type: ignore[union-attr]
        assert "title" in project_dict


class TestTaskModel:
    """Tests for Task model."""

    @pytest.mark.asyncio
    async def test_create_task(
        self,
        test_task: object,
    ) -> None:
        """Test task creation."""
        title = test_task.title  # type: ignore[union-attr]
        assert title == "Test Task"
        status = test_task.status  # type: ignore[union-attr]
        assert status == TaskStatus.PENDING
        priority = test_task.priority  # type: ignore[union-attr]
        assert priority == TASK_PRIORITY_DEFAULT


class TestEnums:
    """Tests for enum types."""

    def test_user_role_values(self) -> None:
        """Test UserRole enum values."""
        assert UserRole.CLIENT.value == "client"
        assert UserRole.MANAGER.value == "manager"
        assert UserRole.PERFORMER.value == "performer"

    def test_project_status_values(self) -> None:
        """Test ProjectStatus enum values."""
        assert ProjectStatus.DRAFT.value == "draft"
        assert ProjectStatus.PENDING.value == "pending"
        assert ProjectStatus.COMPLETED.value == "completed"

    def test_task_status_values(self) -> None:
        """Test TaskStatus enum values."""
        assert TaskStatus.PENDING.value == "pending"
        assert TaskStatus.IN_PROGRESS.value == "in_progress"
        assert TaskStatus.COMPLETED.value == "completed"

    def test_document_type_values(self) -> None:
        """Test DocumentType enum values."""
        assert DocumentType.SOURCE.value == "source"
        assert DocumentType.WORK.value == "work"
        assert DocumentType.RESULT.value == "result"
