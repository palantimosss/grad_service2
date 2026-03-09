"""E2E tests for user workflows."""

from datetime import UTC, datetime

import pytest

from bot.database.crud_modules.project_crud import (
    create_project,
    update_project_status,
)
from bot.database.crud_modules.task_crud import (
    assign_task_to_performer,
    create_task,
    update_task_status,
)
from bot.database.crud_modules.user_crud import (
    create_user,
    get_user_by_telegram_id,
    update_user_profile,
)
from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole


@pytest.mark.asyncio
class TestUserRegistrationFlow:
    """Tests for user registration workflow."""

    async def test_full_registration_flow(
        self,
        test_session: object,
    ) -> None:
        """Test complete user registration."""
        user = await create_user(
            session=test_session,
            params={
                "telegram_id": 987654321,
                "username": "e2euser",
                "first_name": "E2E",
                "last_name": "User",
                "role": UserRole.CLIENT,
            },
        )

        await update_user_profile(
            test_session,
            user.telegram_id,
            params={
                "phone": "+79991112233",
                "email": "e2e@test.com",
                "position": "Manager",
            },
        )

        updated = await get_user_by_telegram_id(
            test_session, user.telegram_id,
        )

        assert updated is not None
        assert updated.phone == "+79991112233"
        assert updated.email == "e2e@test.com"


@pytest.mark.asyncio
class TestProjectWorkflow:
    """Tests for project workflow."""

    async def test_project_creation_to_completion(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test project lifecycle."""
        project = await create_project(
            session=test_session,
            params={
                "title": "Workflow Project",
                "description": "Full workflow test",
                "client_id": test_user.id,  # type: ignore[union-attr]
                "deadline": datetime(2026, 12, 31, tzinfo=UTC),
                "budget": 50000.0,
                "status": ProjectStatus.DRAFT,
            },
        )

        assert project.status == ProjectStatus.DRAFT

        project = await update_project_status(
            test_session,
            project.id,  # type: ignore[union-attr]
            ProjectStatus.IN_PROGRESS,
        )
        assert project.status == ProjectStatus.IN_PROGRESS

        project = await update_project_status(
            test_session,
            project.id,  # type: ignore[union-attr]
            ProjectStatus.COMPLETED,
        )
        assert project.status == ProjectStatus.COMPLETED


@pytest.mark.asyncio
class TestTaskWorkflow:
    """Tests for task workflow."""

    async def test_task_assignment_to_completion(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test task lifecycle."""
        task = await create_task(
            session=test_session,
            params={
                "project_id": test_project.id,  # type: ignore[union-attr]
                "title": "Workflow Task",
                "description": "Task workflow test",
                "performer_id": test_user.id,  # type: ignore[union-attr]
                "manager_id": test_user.id,  # type: ignore[union-attr]
                "deadline": datetime(2026, 6, 30, tzinfo=UTC),
                "priority": 3,
                "status": TaskStatus.PENDING,
            },
        )

        assert task.status == TaskStatus.PENDING

        task = await assign_task_to_performer(
            test_session, task.id, test_user.id,  # type: ignore[union-attr]
        )
        assert task.status == TaskStatus.IN_PROGRESS

        task = await update_task_status(
            test_session,
            task.id,  # type: ignore[union-attr]
            TaskStatus.COMPLETED,
        )
        assert task.status == TaskStatus.COMPLETED
