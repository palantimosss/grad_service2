"""Task CRUD parameters."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from bot.database.models.enums import TaskStatus


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
