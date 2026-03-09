"""Scheduler module for periodic tasks."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler


def create_scheduler() -> AsyncIOScheduler:
    """Create and configure scheduler."""
    return AsyncIOScheduler()


async def check_deadlines() -> None:
    """Check and send deadline notifications."""
