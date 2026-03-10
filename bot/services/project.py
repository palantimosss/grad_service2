"""Project service module."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

    from bot.database.models.enums import ProjectStatus

from bot.database.crud_modules.project_crud import (
    assign_manager_to_project,
    update_project_status,
)
from bot.database.crud_modules.project_crud import (
    create_project as create_project_db,
)


class ProjectServiceParams(TypedDict, total=False):
    """Parameters for project service."""

    client_id: int
    title: str
    description: str | None
    deadline: datetime | None
    budget: float | None
    status: ProjectStatus


async def create_project_service(
    session: AsyncSession,
    project_data: ProjectServiceParams,
) -> object | None:
    """Create a new project."""
    return await create_project_db(
        session=session,
        params=project_data,
    )


async def register_project_service(
    session: AsyncSession,
    project_id: int,
    manager_id: int,
) -> object | None:
    """Register project and assign manager."""
    return await assign_manager_to_project(
        session=session,
        project_id=project_id,
        manager_id=manager_id,
    )


async def change_project_status_service(
    session: AsyncSession,
    project_id: int,
    status: ProjectStatus,
) -> object | None:
    """Change project status."""
    return await update_project_status(
        session=session,
        project_id=project_id,
        status=status,
    )
