"""Project CRUD write operations."""

from typing import TYPE_CHECKING

from sqlalchemy import delete, func, update

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.crud_modules._project_params import ProjectCreateParams

from bot.database.crud_modules._project_read import get_project_by_id
from bot.database.models.enums import ProjectStatus
from bot.database.models.project import Project


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
