"""Unit tests for statistics CRUD operations."""

import pytest

from bot.database.crud_modules.project_crud import create_project
from bot.database.crud_modules.statistics_crud import (
    get_manager_projects_count,
    get_performer_tasks_count,
    get_projects_count_by_status,
    get_tasks_count_by_status,
    get_total_projects_count,
    get_total_tasks_count,
    get_total_users_count,
    get_users_count_by_role,
)
from bot.database.crud_modules.task_crud import create_task
from bot.database.crud_modules.user_crud import create_user
from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole

# Expected counts constants
_EXPECTED_DRAFT_PROJECTS_COUNT = 2
_EXPECTED_CLIENT_USERS_COUNT = 2

# Telegram ID base for test users
_TELEGRAM_ID_BASE = 1000000000

# Field keys
_TITLE_KEY = "title"
_CLIENT_ID_KEY = "client_id"
_STATUS_KEY = "status"
_PROJECT_ID_KEY = "project_id"
_PRIORITY_KEY = "priority"
_TELEGRAM_ID_KEY = "telegram_id"
_USERNAME_KEY = "username"
_FIRST_NAME_KEY = "first_name"
_LAST_NAME_KEY = "last_name"
_ROLE_KEY = "role"


async def _create_project_for_stats(
    session: object,
    client_id: int,
    status: ProjectStatus,
) -> object:
    """Create project for statistics tests."""
    return await create_project(
        session,
        {
            _TITLE_KEY: f"Stats Project {status.value}",
            _CLIENT_ID_KEY: client_id,
            _STATUS_KEY: status,
        },
    )


async def _create_task_for_stats(
    session: object,
    project_id: int,
    status: TaskStatus,
) -> object:
    """Create task for statistics tests."""
    return await create_task(
        session,
        {
            _PROJECT_ID_KEY: project_id,
            _TITLE_KEY: f"Stats Task {status.value}",
            _STATUS_KEY: status,
            _PRIORITY_KEY: 3,
        },
    )


async def _create_user_for_stats(
    session: object,
    role: UserRole,
    telegram_id_offset: int,
) -> object:
    """Create user for statistics tests."""
    return await create_user(
        session,
        {
            _TELEGRAM_ID_KEY: _TELEGRAM_ID_BASE + telegram_id_offset,
            _USERNAME_KEY: f"statsuser_{role.value}",
            _FIRST_NAME_KEY: "Stats",
            _LAST_NAME_KEY: "User",
            _ROLE_KEY: role,
        },
    )


@pytest.mark.asyncio
class TestStatisticsCRUD:
    """Tests for statistics CRUD operations."""

    async def test_get_projects_count_by_status(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting projects count by status."""
        await _create_project_for_stats(
            test_session, test_user.id, ProjectStatus.DRAFT,
        )
        await _create_project_for_stats(
            test_session, test_user.id, ProjectStatus.DRAFT,
        )
        await _create_project_for_stats(
            test_session, test_user.id, ProjectStatus.REGISTERED,
        )
        stats = await get_projects_count_by_status(test_session)
        assert stats[ProjectStatus.DRAFT] == _EXPECTED_DRAFT_PROJECTS_COUNT
        assert stats[ProjectStatus.REGISTERED] == 1

    async def test_get_tasks_count_by_status(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting tasks count by status."""
        await _create_task_for_stats(
            test_session, test_project.id, TaskStatus.PENDING,
        )
        await _create_task_for_stats(
            test_session, test_project.id, TaskStatus.IN_PROGRESS,
        )
        stats = await get_tasks_count_by_status(test_session)
        assert stats[TaskStatus.PENDING] == 1
        assert stats[TaskStatus.IN_PROGRESS] == 1

    async def test_get_users_count_by_role(
        self,
        test_session: object,
    ) -> None:
        """Test getting users count by role."""
        await _create_user_for_stats(
            test_session, UserRole.CLIENT, 1,
        )
        await _create_user_for_stats(
            test_session, UserRole.CLIENT, 2,
        )
        await _create_user_for_stats(
            test_session, UserRole.MANAGER, 3,
        )
        stats = await get_users_count_by_role(test_session)
        assert stats[UserRole.CLIENT] == _EXPECTED_CLIENT_USERS_COUNT
        assert stats[UserRole.MANAGER] == 1

    async def test_get_total_projects_count(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting total projects count."""
        initial = await get_total_projects_count(test_session)
        await _create_project_for_stats(
            test_session, test_user.id, ProjectStatus.DRAFT,
        )
        final = await get_total_projects_count(test_session)
        assert final == initial + 1

    async def test_get_total_tasks_count(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting total tasks count."""
        initial = await get_total_tasks_count(test_session)
        await _create_task_for_stats(
            test_session, test_project.id, TaskStatus.PENDING,
        )
        final = await get_total_tasks_count(test_session)
        assert final == initial + 1

    async def test_get_total_users_count(
        self,
        test_session: object,
    ) -> None:
        """Test getting total users count."""
        initial = await get_total_users_count(test_session)
        await _create_user_for_stats(
            test_session, UserRole.CLIENT, 4,
        )
        final = await get_total_users_count(test_session)
        assert final == initial + 1

    async def test_get_manager_projects_count(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting manager projects count."""
        await _create_project_for_stats(
            test_session, test_user.id, ProjectStatus.DRAFT,
        )
        count = await get_manager_projects_count(test_session, test_user.id)
        assert count >= 1

    async def test_get_performer_tasks_count(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting performer tasks count."""
        await _create_task_for_stats(
            test_session, test_project.id, TaskStatus.PENDING,
        )
        count = await get_performer_tasks_count(test_session, test_user.id)
        assert count >= 1
