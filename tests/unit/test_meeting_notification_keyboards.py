"""Tests for meeting, notification, and client keyboards."""

from bot.keyboards._clients import (
    get_clients_keyboard,
    get_notification_keyboard,
)
from bot.keyboards._meetings import get_meeting_response_keyboard

# Constants for test assertions
_BACK_BUTTON = "Назад"


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
class MockCompany:
    """Mock company for tests."""

    def __init__(self, obj_id: int, name: str):
        self.id = obj_id
        self.name = name


class TestMeetingResponseKeyboard:
    """Tests for meeting response keyboard."""

    def test_get_meeting_response_keyboard(self) -> None:
        """Test meeting response keyboard creation."""
        keyboard = get_meeting_response_keyboard(1)
        _assert_keyboard_has_buttons(keyboard, ["Подтвердить", "Отклонить"])


class TestClientsKeyboard:
    """Tests for clients keyboard."""

    def test_get_clients_keyboard(self) -> None:
        """Test clients keyboard creation."""
        companies = [
            MockCompany(1, "Company 1"),
            MockCompany(2, "Company 2"),
        ]
        keyboard = get_clients_keyboard(companies)
        _assert_keyboard_has_buttons(
            keyboard,
            ["🏢 Company 1", "🏢 Company 2", "Добавить клиента", _BACK_BUTTON],
        )


class TestNotificationKeyboard:
    """Tests for notification keyboard."""

    def test_get_notification_keyboard(self) -> None:
        """Test notification keyboard creation."""
        keyboard = get_notification_keyboard(1)
        _assert_keyboard_has_buttons(
            keyboard, ["Отметить прочитанным", _BACK_BUTTON],
        )
