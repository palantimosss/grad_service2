"""Project CRUD parameters."""

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from datetime import datetime

    from bot.database.models.enums import ProjectStatus


class ProjectCreateParams(TypedDict, total=False):
    """Parameters for creating a project."""

    title: str
    description: str | None
    client_id: int
    deadline: datetime | None
    budget: float | None
    status: ProjectStatus
