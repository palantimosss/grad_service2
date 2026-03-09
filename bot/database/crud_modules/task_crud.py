"""Task CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.enums import TaskStatus
from bot.database.models.task import Task


class TaskCreateParams(TypedDict, total=False):
    """Parameters for creating a task."""

    project_id: int
    title: str
    description: str | None
    performer_id: int | None
    manager_id: int | None
    deadline: datetime | None
    priority: int
    status: TaskStatus


async def get_task_by_id(
    session: AsyncSession, task_id: int,
) -> Task | None:
    """Get task by ID."""
    query_result = await session.execute(
        select(Task).where(Task.id == task_id),
    )
    return query_result.scalar_one_or_none()


async def get_tasks_by_project_id(
    session: AsyncSession, project_id: int,
) -> list[Task]:
    """Get tasks by project ID."""
    query_result = await session.execute(
        select(Task).where(Task.project_id == project_id),
    )
    return list(query_result.scalars().all())


async def get_tasks_by_performer_id(
    session: AsyncSession, performer_id: int,
) -> list[Task]:
    """Get tasks by performer ID."""
    query_result = await session.execute(
        select(Task).where(Task.performer_id == performer_id),
    )
    return list(query_result.scalars().all())


async def get_tasks_by_status(
    session: AsyncSession, status: TaskStatus,
) -> list[Task]:
    """Get tasks by status."""
    query_result = await session.execute(
        select(Task).where(Task.status == status),
    )
    return list(query_result.scalars().all())


async def create_task(
    session: AsyncSession, task_data: TaskCreateParams,
) -> Task:
    """Create a new task."""
    task = Task(**task_data)
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task


async def update_task_status(
    session: AsyncSession,
    task_id: int,
    status: TaskStatus,
) -> Task | None:
    """Update task status."""
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(status=status),
    )
    await session.commit()
    return await get_task_by_id(session, task_id)


async def assign_task_to_performer(
    session: AsyncSession,
    task_id: int,
    performer_id: int,
) -> Task | None:
    """Assign task to performer."""
    await session.execute(
        update(Task)
        .where(Task.id == task_id)
        .values(performer_id=performer_id, status=TaskStatus.IN_PROGRESS),
    )
    await session.commit()
    return await get_task_by_id(session, task_id)


async def delete_task(
    session: AsyncSession, task_id: int,
) -> bool:
    """Delete task by ID."""
    query_result = await session.execute(
        delete(Task).where(Task.id == task_id),
    )
    await session.commit()
    return query_result.rowcount > 0


async def get_pending_tasks(session: AsyncSession) -> list[Task]:
    """Get pending tasks."""
    query_result = await session.execute(
        select(Task).where(Task.status == TaskStatus.PENDING),
    )
    return list(query_result.scalars().all())


async def get_all_tasks(session: AsyncSession) -> list[Task]:
    """Get all tasks."""
    query_result = await session.execute(select(Task))
    return list(query_result.scalars().all())
