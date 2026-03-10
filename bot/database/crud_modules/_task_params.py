"""Task CRUD parameters."""

from datetime import datetime  # noqa: TC003
from typing import TypedDict

from bot.database.models.enums import TaskStatus  # noqa: TC001


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
