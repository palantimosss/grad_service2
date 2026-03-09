"""Stage CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.stage import ProjectStage


class StageCreateParams(TypedDict, total=False):
    """Parameters for creating a stage."""

    project_id: int
    title: str
    description: str | None
    order: int
    planned_start: datetime | None
    planned_end: datetime | None
    status: str


async def get_stage_by_id(
    session: AsyncSession, stage_id: int,
) -> ProjectStage | None:
    """Get stage by ID."""
    result = await session.execute(
        select(ProjectStage).where(ProjectStage.id == stage_id),
    )
    return result.scalar_one_or_none()


async def get_stages_by_project_id(
    session: AsyncSession, project_id: int,
) -> list[ProjectStage]:
    """Get stages by project ID."""
    result = await session.execute(
        select(ProjectStage)
        .where(ProjectStage.project_id == project_id)
        .order_by(ProjectStage.order),
    )
    return list(result.scalars().all())


async def create_stage(
    session: AsyncSession, params: StageCreateParams,
) -> ProjectStage:
    """Create a new stage."""
    stage = ProjectStage(**params)
    session.add(stage)
    await session.commit()
    await session.refresh(stage)
    return stage


async def update_stage_status(
    session: AsyncSession,
    stage_id: int,
    status: str,
) -> ProjectStage | None:
    """Update stage status."""
    await session.execute(
        update(ProjectStage)
        .where(ProjectStage.id == stage_id)
        .values(status=status),
    )
    await session.commit()
    return await get_stage_by_id(session, stage_id)


async def delete_stage(
    session: AsyncSession, stage_id: int,
) -> bool:
    """Delete stage by ID."""
    result = await session.execute(
        delete(ProjectStage).where(ProjectStage.id == stage_id),
    )
    await session.commit()
    return result.rowcount > 0
