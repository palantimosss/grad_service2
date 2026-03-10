"""Statistics CRUD operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import func, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.enums import ProjectStatus, TaskStatus, UserRole

from bot.database.models.project import Project
from bot.database.models.task import Task
from bot.database.models.user import User


async def get_projects_count_by_status(
    session: AsyncSession,
) -> dict[ProjectStatus, int]:
    """Get count of projects by status."""
    query_result = await session.execute(
        select(Project.status, func.count(Project.id)).group_by(
            Project.status,
        ),
    )
    return {row[0]: row[1] for row in query_result.all()}


async def get_tasks_count_by_status(
    session: AsyncSession,
) -> dict[TaskStatus, int]:
    """Get count of tasks by status."""
    query_result = await session.execute(
        select(Task.status, func.count(Task.id)).group_by(Task.status),
    )
    return {row[0]: row[1] for row in query_result.all()}


async def get_users_count_by_role(
    session: AsyncSession,
) -> dict[UserRole, int]:
    """Get count of users by role."""
    query_result = await session.execute(
        select(User.role, func.count(User.id)).group_by(User.role),
    )
    return {row[0]: row[1] for row in query_result.all()}


async def get_total_projects_count(session: AsyncSession) -> int:
    """Get total count of projects."""
    query_result = await session.execute(select(func.count(Project.id)))
    return query_result.scalar() or 0


async def get_total_tasks_count(session: AsyncSession) -> int:
    """Get total count of tasks."""
    query_result = await session.execute(select(func.count(Task.id)))
    return query_result.scalar() or 0


async def get_total_users_count(session: AsyncSession) -> int:
    """Get total count of users."""
    query_result = await session.execute(select(func.count(User.id)))
    return query_result.scalar() or 0


async def get_manager_projects_count(
    session: AsyncSession,
    manager_id: int,
) -> int:
    """Get count of projects for manager."""
    query_result = await session.execute(
        select(func.count(Project.id)).where(Project.manager_id == manager_id),
    )
    return query_result.scalar() or 0


async def get_performer_tasks_count(
    session: AsyncSession,
    performer_id: int,
) -> int:
    """Get count of tasks for performer."""
    query_result = await session.execute(
        select(func.count(Task.id)).where(Task.performer_id == performer_id),
    )
    return query_result.scalar() or 0
