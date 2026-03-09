"""Calendar service module for meetings."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.crud_modules.meeting_crud import (
    add_meeting_participant as add_participant_db,
)
from bot.database.crud_modules.meeting_crud import (
    create_meeting as create_meeting_db,
)
from bot.database.crud_modules.meeting_crud import (
    update_meeting_status as update_meeting_status_db,
)
from bot.database.models.enums import MeetingStatus


class MeetingServiceParams(TypedDict, total=False):
    """Parameters for meeting service."""

    project_id: int
    title: str
    organizer_id: int
    scheduled_at: datetime
    description: str | None
    duration_minutes: int
    address: str | None
    coordinates: str | None
    is_online: bool
    online_link: str | None
    gis_check_result: str | None


async def create_meeting_service(
    session: AsyncSession,
    meeting_data: MeetingServiceParams,
) -> object | None:
    """Create a new meeting."""
    return await create_meeting_db(session=session, params=meeting_data)


async def confirm_meeting_service(
    session: AsyncSession,
    meeting_id: int,
) -> object | None:
    """Confirm meeting."""
    return await update_meeting_status_db(
        session=session,
        meeting_id=meeting_id,
        status=MeetingStatus.CONFIRMED,
    )


async def cancel_meeting_service(
    session: AsyncSession,
    meeting_id: int,
) -> object | None:
    """Cancel meeting."""
    return await update_meeting_status_db(
        session=session,
        meeting_id=meeting_id,
        status=MeetingStatus.CANCELLED,
    )


async def complete_meeting_service(
    session: AsyncSession,
    meeting_id: int,
) -> object | None:
    """Complete meeting."""
    return await update_meeting_status_db(
        session=session,
        meeting_id=meeting_id,
        status=MeetingStatus.COMPLETED,
    )


async def add_participant_service(
    session: AsyncSession,
    meeting_id: int,
    user_id: int,
) -> object | None:
    """Add participant to meeting."""
    return await add_participant_db(
        session=session,
        meeting_id=meeting_id,
        user_id=user_id,
    )
