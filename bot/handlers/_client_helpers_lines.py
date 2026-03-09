"""Client helpers - project line helpers."""


def _get_description_line(project: object) -> str:
    """Get description line."""
    description = project.description or "Нет"
    return f"Описание: {description}"


def _get_deadline_line(project: object) -> str:
    """Get deadline line."""
    deadline = project.deadline or "Не установлен"
    return f"Дедлайн: {deadline}"


def _get_budget_line(project: object) -> str:
    """Get budget line."""
    budget = project.budget or "Не указан"
    return f"Бюджет: {budget}"


def _get_client_name(project: object) -> str:
    """Get client name from project."""
    return project.client.first_name if project.client else "Не назначен"


def _get_manager_name(project: object) -> str:
    """Get manager name from project."""
    return project.manager.first_name if project.manager else "Не назначен"
