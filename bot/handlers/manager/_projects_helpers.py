"""Project handlers helper functions - text formatting."""

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


def get_status_text(status_value: str) -> str:
    """Get status text from status value."""
    for key, label in STATUS_MAP:
        if key == status_value:
            return label
    return status_value


def get_client_name(project: object) -> str:
    """Get client name from project."""
    return project.client.first_name if project.client else "Не назначен"


def get_manager_name(project: object) -> str:
    """Get manager name from project."""
    return project.manager.first_name if project.manager else "Не назначен"


def get_project_info_lines(project: object, status_text: str) -> list[str]:
    """Get project info lines."""
    client_name = get_client_name(project)
    manager_name = get_manager_name(project)
    description = project.description or "Нет"
    deadline = project.deadline or "Не установлен"
    budget = project.budget or "Не указан"
    return [
        f"<b>{project.title}</b>",
        "",
        f"Статус: {status_text}",
        f"Клиент: {client_name}",
        f"Руководитель: {manager_name}",
        f"Описание: {description}",
        f"Дедлайн: {deadline}",
        f"Бюджет: {budget}",
    ]


def build_project_text(project: object, status_text: str) -> str:
    """Build project detail text."""
    lines = get_project_info_lines(project, status_text)
    return "\n".join(lines)
