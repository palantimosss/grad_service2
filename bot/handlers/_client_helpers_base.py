"""Client helpers - status and parsing functions."""

from __future__ import annotations

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
