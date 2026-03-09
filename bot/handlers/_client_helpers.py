"""Client handlers helper functions."""

from datetime import UTC, datetime

# Skip option text
_SKIP_OPTION = "пропустить"

# Status map for display (immutable tuple)
STATUS_MAP = (
    ("draft", "Черновик"),
    ("pending", "На регистрации"),
    ("registered", "Зарегистрирован"),
    ("in_progress", "В работе"),
    ("on_hold", "Приостановлен"),
    ("completed", "Завершён"),
    ("archived", "Архив"),
)


def get_skip_option() -> str:
    """Get skip option text."""
    return _SKIP_OPTION


def get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, label in STATUS_MAP:
        if key == status_value:
            return label
    return status_value


def parse_deadline(text: str) -> datetime | None:
    """Parse deadline from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return datetime.strptime(text, "%d.%m.%Y %H:%M").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def parse_budget(text: str) -> float | None:
    """Parse budget from text."""
    if text == _SKIP_OPTION:
        return None
    try:
        return float(text.replace(",", "."))
    except ValueError:
        return None


def format_project_text(project: object) -> str:
    """Format project text for display."""
    status_text = get_status_text(project.status.value)
    lines = _get_project_lines(project, status_text)
    return "\n".join(lines)


def _get_project_lines(project: object, status_text: str) -> list[str]:
    """Get project info lines."""
    client_name = _get_client_name(project)
    manager_name = _get_manager_name(project)
    return [
        f"<b>{project.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Клиент: {client_name}",
        f"Руководитель: {manager_name}",
        f"Описание: {project.description or 'Нет'}",
        f"Дедлайн: {project.deadline or 'Не установлен'}",
        f"Бюджет: {project.budget or 'Не указан'}",
    ]


def _get_client_name(project: object) -> str:
    """Get client name from project."""
    return project.client.first_name if project.client else "Не назначен"


def _get_manager_name(project: object) -> str:
    """Get manager name from project."""
    return project.manager.first_name if project.manager else "Не назначен"
