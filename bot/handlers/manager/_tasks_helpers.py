"""Task handlers helper functions."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from bot.database.crud_modules.task_crud import create_task
from bot.database.models.enums import TaskStatus

if TYPE_CHECKING:
    from aiogram import types

# Skip option text
SKIP_OPTION = "пропустить"

# Default values
DEFAULT_TASK_PRIORITY = 3


def get_skip_option() -> str:
    """Get skip option text."""
    return SKIP_OPTION


def parse_datetime(text: str, fmt: str) -> datetime | None:
    """Parse datetime from text."""
    if text == SKIP_OPTION:
        return None
    try:
        return datetime.strptime(text, fmt).replace(tzinfo=UTC)
    except ValueError:
        return None


def build_performers_text(performers: list) -> str:
    """Build performers selection text."""
    lines = ["Выберите исполнителя (ID):"]
    lines.extend(
        f"{performer.id} - {performer.first_name}"
        for performer in performers
    )
    lines.append("Или введите ID вручную:")
    return "\n".join(lines)


def build_task_params(
    task_data: dict,
    user_id: int,
    priority: int,
) -> dict:
    """Build task creation params."""
    task_params: dict = {
        "project_id": task_data["project_id"],
        "title": task_data["title"],
        "performer_id": task_data.get("performer_id"),
        "manager_id": user_id,
        "priority": priority,
        "status": TaskStatus.PENDING,
    }
    if task_data.get("description"):
        task_params["description"] = task_data["description"]
    if task_data.get("deadline"):
        task_params["deadline"] = task_data["deadline"]
    return task_params


def get_callback_data_str(callback: types.CallbackQuery) -> str:
    """Get callback data string."""
    return callback.data or ""


def get_project_id_from_callback(callback: types.CallbackQuery) -> int:
    """Extract project ID from callback."""
    parts = get_callback_data_str(callback).split("_")
    return int(parts[2])


async def create_task_in_db(
    session: object,
    user_id: int,
    task_data: dict,
    priority: int,
) -> None:
    """Create task in database."""
    task_params = build_task_params(task_data, user_id, priority)
    await create_task(session=session, params=task_params)
