"""Project CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, func, select, update

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.enums import ProjectStatus
from bot.database.models.project import Project


class ProjectCreateParams(TypedDict, total=False):
    """Parameters for creating a project."""

    title: str
    description: str | None
    client_id: int
    deadline: datetime | None
    budget: float | None
    status: ProjectStatus


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


async def create_project(
    session: AsyncSession, project_data: ProjectCreateParams,
) -> Project:
    """Create a new project."""
    project = Project(**project_data)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project


async def update_project_status(
    session: AsyncSession,
    project_id: int,
    status: ProjectStatus,
) -> Project | None:
    """Update project status."""
    await session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(status=status, updated_at=func.now()),
    )
    await session.commit()
    return await get_project_by_id(session, project_id)


async def assign_manager_to_project(
    session: AsyncSession,
    project_id: int,
    manager_id: int,
) -> Project | None:
    """Assign manager to project."""
    await session.execute(
        update(Project)
        .where(Project.id == project_id)
        .values(manager_id=manager_id, status=ProjectStatus.REGISTERED),
    )
    await session.commit()
    return await get_project_by_id(session, project_id)


async def delete_project(
    session: AsyncSession, project_id: int,
) -> bool:
    """Delete project by ID."""
    query_result = await session.execute(
        delete(Project).where(Project.id == project_id),
    )
    await session.commit()
    return query_result.rowcount > 0


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
