"""GIS check log CRUD operations."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.gis_log import GISCheckLog


class GISLogCreateParams(TypedDict):
    """Parameters for creating a GIS log."""

    meeting_id: int
    address: str
    coordinates: str | None
    inside_zone: bool


async def create_gis_check_log(
    session: AsyncSession, params: GISLogCreateParams,
) -> GISCheckLog:
    """Create a new GIS check log."""
    log = GISCheckLog(
        **params,
        checked_at=datetime.now(tz=UTC),
    )
    session.add(log)
    await session.commit()
    await session.refresh(log)
    return log


async def get_gis_logs_by_meeting_id(
    session: AsyncSession, meeting_id: int,
) -> list[GISCheckLog]:
    """Get GIS logs by meeting ID."""
    result = await session.execute(
        select(GISCheckLog).where(GISCheckLog.meeting_id == meeting_id),
    )
    return list(result.scalars().all())


async def delete_gis_log(
    session: AsyncSession, log_id: int,
) -> bool:
    """Delete GIS log by ID."""
    result = await session.execute(
        delete(GISCheckLog).where(GISCheckLog.id == log_id),
    )
    await session.commit()
    return result.rowcount > 0
