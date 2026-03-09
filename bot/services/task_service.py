"""Task service module."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud_modules.task_crud import (
    assign_task_to_performer,
    update_task_status,
)
from bot.database.crud_modules.task_crud import (
    create_task as create_task_db,
)
from bot.database.models.enums import TaskStatus


class TaskServiceParams(TypedDict, total=False):
    """Parameters for task service."""

    project_id: int
    title: str
    description: str | None
    performer_id: int | None
    manager_id: int | None
    deadline: datetime | None
    priority: int
    status: TaskStatus


async def create_task_service(
    session: AsyncSession,
    params: TaskServiceParams,
) -> object | None:
    """Create a new task."""
    return await create_task_db(
        session=session,
        params=params,
    )


async def assign_task_service(
    session: AsyncSession,
    task_id: int,
    performer_id: int,
) -> object | None:
    """Assign task to performer."""
    return await assign_task_to_performer(
        session=session,
        task_id=task_id,
        performer_id=performer_id,
    )


async def complete_task_service(
    session: AsyncSession,
    task_id: int,
) -> object | None:
    """Mark task as completed."""
    return await update_task_status(
        session=session,
        task_id=task_id,
        status=TaskStatus.COMPLETED,
    )
