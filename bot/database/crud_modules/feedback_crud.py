"""Feedback CRUD operations."""

from typing import TYPE_CHECKING, TypedDict

from sqlalchemy import delete, select

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models.feedback import Feedback


class FeedbackCreateParams(TypedDict):
    """Parameters for creating a feedback."""

    project_id: int
    author_id: int
    message: str
    rating: int | None


async def get_feedback_by_id(
    session: AsyncSession, feedback_id: int,
) -> Feedback | None:
    """Get feedback by ID."""
    result = await session.execute(
        select(Feedback).where(Feedback.id == feedback_id),
    )
    return result.scalar_one_or_none()


async def get_feedbacks_by_project_id(
    session: AsyncSession, project_id: int,
) -> list[Feedback]:
    """Get feedbacks by project ID."""
    result = await session.execute(
        select(Feedback).where(Feedback.project_id == project_id),
    )
    return list(result.scalars().all())


async def create_feedback(
    session: AsyncSession, params: FeedbackCreateParams,
) -> Feedback:
    """Create a new feedback."""
    feedback = Feedback(**params)
    session.add(feedback)
    await session.commit()
    await session.refresh(feedback)
    return feedback


async def delete_feedback(
    session: AsyncSession, feedback_id: int,
) -> bool:
    """Delete feedback by ID."""
    result = await session.execute(
        delete(Feedback).where(Feedback.id == feedback_id),
    )
    await session.commit()
    return result.rowcount > 0
