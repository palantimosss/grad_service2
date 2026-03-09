"""Tests for task keyboards."""

from bot.database.models.enums import TaskStatus
from bot.keyboards._tasks import (
    get_task_actions_keyboard,
    get_tasks_keyboard,
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
class MockTask:
    """Mock task for tests."""

    def __init__(self, obj_id: int, title: str, status: TaskStatus):
        self.id = obj_id
        self.title = title
        self.status = status


class TestTasksKeyboard:
    """Tests for tasks keyboard."""

    def test_get_tasks_keyboard_empty(self) -> None:
        """Test tasks keyboard with empty list."""
        keyboard = get_tasks_keyboard([])
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons

    def test_get_tasks_keyboard_with_tasks(self) -> None:
        """Test tasks keyboard with tasks list."""
        tasks = [
            MockTask(1, "Task 1", TaskStatus.PENDING),
            MockTask(2, "Task 2", TaskStatus.COMPLETED),
        ]
        keyboard = get_tasks_keyboard(tasks)
        _assert_keyboard_has_buttons(
            keyboard, ["⏳ Task 1", "✅ Task 2", _BACK_BUTTON],
        )


class TestTaskActionsKeyboard:
    """Tests for task actions keyboard."""

    def test_get_task_actions_keyboard_pending(self) -> None:
        """Test task actions keyboard for pending task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.PENDING)
        _assert_keyboard_has_buttons(
            keyboard, ["Взять в работу", _UPLOAD_DOC_BUTTON],
        )

    def test_get_task_actions_keyboard_in_progress(self) -> None:
        """Test task actions keyboard for in_progress task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.IN_PROGRESS)
        _assert_keyboard_has_buttons(
            keyboard, ["Завершить", _UPLOAD_DOC_BUTTON],
        )
