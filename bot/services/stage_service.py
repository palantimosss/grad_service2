"""Stage service module."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud_modules.stage_crud import (
    create_stage as create_stage_db,
)
from bot.database.crud_modules.stage_crud import (
    update_stage_status,
)


class StageServiceParams(TypedDict, total=False):
    """Parameters for stage service."""

    project_id: int
    title: str
    description: str | None
    order: int
    planned_start: datetime | None
    planned_end: datetime | None


async def create_stage_service(
    session: AsyncSession,
    stage_data: StageServiceParams,
) -> object | None:
    """Create a new project stage."""
    return await create_stage_db(
        session=session,
        params=stage_data,
    )


async def complete_stage_service(
    session: AsyncSession,
    stage_id: int,
) -> object | None:
    """Mark stage as completed."""
    return await update_stage_status(
        session=session,
        stage_id=stage_id,
        status="completed",
    )
