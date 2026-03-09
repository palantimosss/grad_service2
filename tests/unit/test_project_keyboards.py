"""Tests for project keyboards."""

from bot.database.models.enums import UserRole
from bot.keyboards._projects import (
    get_project_actions_keyboard,
    get_project_status_keyboard,
    get_projects_keyboard,
)

# Constants for test assertions
_BACK_BUTTON = "Назад"
_UPLOAD_DOC_BUTTON = "Загрузить документ"


def _get_keyboard_buttons(keyboard: object) -> list[str]:
    """Extract button texts from keyboard."""
    return [
        button.text
        for row in keyboard.inline_keyboard  # type: ignore[attr-defined]
        for button in row
    ]


def _assert_keyboard_has_buttons(
    keyboard: object, expected_buttons: list[str],
) -> None:
    """Assert keyboard has expected buttons."""
    buttons = _get_keyboard_buttons(keyboard)
    for expected in expected_buttons:
        assert expected in buttons


# Mock class for tests
class MockProject:
    """Mock project for tests."""

    def __init__(self, obj_id: int, title: str):
        self.id = obj_id
        self.title = title


class TestProjectsKeyboard:
    """Tests for projects keyboard."""

    def test_get_projects_keyboard_empty(self) -> None:
        """Test projects keyboard with empty list."""
        keyboard = get_projects_keyboard([])
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons

    def test_get_projects_keyboard_with_projects(self) -> None:
        """Test projects keyboard with projects list."""
        projects = [
            MockProject(1, "Project 1"),
            MockProject(2, "Project 2"),
        ]
        keyboard = get_projects_keyboard(projects)
        _assert_keyboard_has_buttons(
            keyboard, ["📁 Project 1", "📁 Project 2", _BACK_BUTTON],
        )


class TestProjectActionsKeyboard:
    """Tests for project actions keyboard."""

    def test_get_project_actions_keyboard_client(self) -> None:
        """Test project actions keyboard for client."""
        keyboard = get_project_actions_keyboard(1, UserRole.CLIENT)
        _assert_keyboard_has_buttons(
            keyboard, [_UPLOAD_DOC_BUTTON, "Обратная связь"],
        )

    def test_get_project_actions_keyboard_manager(self) -> None:
        """Test project actions keyboard for manager."""
        keyboard = get_project_actions_keyboard(1, UserRole.MANAGER)
        _assert_keyboard_has_buttons(
            keyboard, ["Создать задачу", "Создать этап", "Создать встречу"],
        )

    def test_get_project_actions_keyboard_performer(self) -> None:
        """Test project actions keyboard for performer."""
        keyboard = get_project_actions_keyboard(1, UserRole.PERFORMER)
        buttons = _get_keyboard_buttons(keyboard)
        assert _UPLOAD_DOC_BUTTON in buttons


class TestProjectStatusKeyboard:
    """Tests for project status keyboard."""

    def test_get_project_status_keyboard(self) -> None:
        """Test project status keyboard creation."""
        keyboard = get_project_status_keyboard(1)
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons
        assert len(buttons) > 1  # At least some status buttons
