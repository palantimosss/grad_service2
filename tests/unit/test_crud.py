"""Unit tests for CRUD operations."""

import pytest

from bot.database.crud_modules.project_crud import (
    get_project_by_id,
    update_project_status,
)
from bot.database.crud_modules.task_crud import (
    get_task_by_id,
    update_task_status,
)
from bot.database.crud_modules.user_crud import (
    get_user_by_id,
    get_user_by_telegram_id,
    update_user_role,
)
from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole


@pytest.mark.asyncio
class TestUserCRUD:
    """Tests for user CRUD operations."""

    async def test_get_user_by_telegram_id(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting user by Telegram ID."""
        user = await get_user_by_telegram_id(
            test_session, test_user.telegram_id,  # type: ignore[union-attr]
        )
        assert user is not None
        assert user.id == test_user.id  # type: ignore[union-attr]

    async def test_get_user_by_id(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting user by internal ID."""
        user = await get_user_by_id(
            test_session, test_user.id,  # type: ignore[union-attr]
        )
        assert user is not None
        tid = user.telegram_id  # type: ignore[union-attr]
        assert tid == test_user.telegram_id  # type: ignore[union-attr]

    async def test_update_user_role(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test updating user role."""
        updated = await update_user_role(
            test_session,
            test_user.telegram_id,  # type: ignore[union-attr]
            UserRole.MANAGER,
        )
        assert updated is not None
        assert updated.role == UserRole.MANAGER


@pytest.mark.asyncio
class TestProjectCRUD:
    """Tests for project CRUD operations."""

    async def test_get_project_by_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting project by ID."""
        project = await get_project_by_id(
            test_session, test_project.id,  # type: ignore[union-attr]
        )
        assert project is not None
        title = project.title  # type: ignore[union-attr]
        assert title == test_project.title  # type: ignore[union-attr]

    async def test_update_project_status(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test updating project status."""
        updated = await update_project_status(
            test_session,
            test_project.id,  # type: ignore[union-attr]
            ProjectStatus.IN_PROGRESS,
        )
        assert updated is not None
        status = updated.status  # type: ignore[union-attr]
        assert status == ProjectStatus.IN_PROGRESS


@pytest.mark.asyncio
class TestTaskCRUD:
    """Tests for task CRUD operations."""

    async def test_get_task_by_id(
        self,
        test_session: object,
        test_task: object,
    ) -> None:
        """Test getting task by ID."""
        task = await get_task_by_id(
            test_session, test_task.id,  # type: ignore[union-attr]
        )
        assert task is not None
        title = task.title  # type: ignore[union-attr]
        assert title == test_task.title  # type: ignore[union-attr]

    async def test_update_task_status(
        self,
        test_session: object,
        test_task: object,
    ) -> None:
        """Test updating task status."""
        updated = await update_task_status(
            test_session,
            test_task.id,  # type: ignore[union-attr]
            TaskStatus.IN_PROGRESS,
        )
        assert updated is not None
        status = updated.status  # type: ignore[union-attr]
        assert status == TaskStatus.IN_PROGRESS
