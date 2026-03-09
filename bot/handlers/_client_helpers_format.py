"""Client helpers - project text formatting."""

from bot.handlers._client_helpers_base import get_status_text
from bot.handlers._client_helpers_lines import (
    _get_budget_line,
    _get_client_line,
    _get_deadline_line,
    _get_description_line,
    _get_manager_line,
)


def format_project_text(project: object) -> str:
    """Format project text for display."""
    status_text = get_status_text(project.status.value)
    lines = _get_project_lines(project, status_text)
    return "\n".join(lines)


def _get_project_lines(project: object, status_text: str) -> list[str]:
    """Get project info lines."""
    return [
        _get_title_line(project),
        "",
        _get_status_line(status_text),
        _get_client_line(project),
        _get_manager_line(project),
        _get_description_line(project),
        _get_deadline_line(project),
        _get_budget_line(project),
    ]


def _get_title_line(project: object) -> str:
    """Get title line."""
    return f"<b>{project.title}</b>"


def _get_status_line(status_text: str) -> str:
    """Get status line."""
    return f"Статус: {status_text}"
