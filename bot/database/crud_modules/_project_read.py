"""Project CRUD read operations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.enums import ProjectStatus
from bot.database.models.project import Project


async def get_project_by_id(
    session: AsyncSession, project_id: int,
) -> Project | None:
    """Get project by ID."""
    query_result = await session.execute(
        select(Project).where(Project.id == project_id),
    )
    return query_result.scalar_one_or_none()


async def get_projects_by_client_id(
    session: AsyncSession, client_id: int,
) -> list[Project]:
    """Get projects by client ID."""
    query_result = await session.execute(
        select(Project).where(Project.client_id == client_id),
    )
    return list(query_result.scalars().all())


async def get_projects_by_manager_id(
    session: AsyncSession, manager_id: int,
) -> list[Project]:
    """Get projects by manager ID."""
    query_result = await session.execute(
        select(Project).where(Project.manager_id == manager_id),
    )
    return list(query_result.scalars().all())


async def get_projects_by_status(
    session: AsyncSession, status: ProjectStatus,
) -> list[Project]:
    """Get projects by status."""
    query_result = await session.execute(
        select(Project).where(Project.status == status),
    )
    return list(query_result.scalars().all())


async def get_all_projects(session: AsyncSession) -> list[Project]:
    """Get all projects."""
    query_result = await session.execute(select(Project))
    return list(query_result.scalars().all())


async def get_pending_projects(
    session: AsyncSession,
) -> list[Project]:
    """Get pending projects."""
    query_result = await session.execute(
        select(Project).where(Project.status == ProjectStatus.PENDING),
    )
    return list(query_result.scalars().all())
