"""Meeting CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select, update
from sqlalchemy.orm import selectinload

if TYPE_CHECKING:
    from datetime import datetime

    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.enums import MeetingParticipantStatus, MeetingStatus
from bot.database.models.meeting import Meeting, MeetingParticipant


class MeetingCreateParams(TypedDict, total=False):
    """Parameters for creating a meeting."""

    project_id: int
    title: str
    description: str | None
    organizer_id: int
    scheduled_at: datetime
    duration_minutes: int
    address: str | None
    coordinates: str | None
    is_online: bool
    online_link: str | None
    gis_check_result: str | None


async def get_meeting_by_id(
    session: AsyncSession, meeting_id: int,
) -> Meeting | None:
    """Get meeting by ID."""
    result = await session.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id),
    )
    return result.scalar_one_or_none()


async def get_meetings_by_project_id(
    session: AsyncSession, project_id: int,
) -> list[Meeting]:
    """Get meetings by project ID."""
    result = await session.execute(
        select(Meeting).where(Meeting.project_id == project_id),
    )
    return list(result.scalars().all())


async def create_meeting(
    session: AsyncSession, params: MeetingCreateParams,
) -> Meeting:
    """Create a new meeting."""
    meeting = Meeting(**params)
    session.add(meeting)
    await session.commit()
    await session.refresh(meeting)
    return meeting


async def update_meeting_status(
    session: AsyncSession,
    meeting_id: int,
    status: MeetingStatus,
) -> Meeting | None:
    """Update meeting status."""
    await session.execute(
        update(Meeting)
        .where(Meeting.id == meeting_id)
        .values(status=status),
    )
    await session.commit()
    return await get_meeting_by_id(session, meeting_id)


async def delete_meeting(
    session: AsyncSession, meeting_id: int,
) -> bool:
    """Delete meeting by ID."""
    result = await session.execute(
        delete(Meeting).where(Meeting.id == meeting_id),
    )
    await session.commit()
    return result.rowcount > 0


async def add_meeting_participant(
    session: AsyncSession,
    meeting_id: int,
    user_id: int,
    status: MeetingParticipantStatus | None = None,
) -> MeetingParticipant:
    """Add participant to meeting."""
    if status is None:
        status = MeetingParticipantStatus.PENDING

    participant = MeetingParticipant(
        meeting_id=meeting_id,
        user_id=user_id,
        status=status,
    )
    session.add(participant)
    await session.commit()
    await session.refresh(participant)
    return participant


async def update_participant_status(
    session: AsyncSession,
    meeting_id: int,
    user_id: int,
    status: MeetingParticipantStatus,
) -> MeetingParticipant | None:
    """Update participant status."""
    result = await session.execute(
        select(MeetingParticipant).where(
            MeetingParticipant.meeting_id == meeting_id,
            MeetingParticipant.user_id == user_id,
        ),
    )
    participant = result.scalar_one_or_none()
    if participant:
        participant.status = status
        await session.commit()
        await session.refresh(participant)
    return participant
