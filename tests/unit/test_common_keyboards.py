"""Tests for common keyboards: back, yes/no, cancel."""

from bot.keyboards._common import (
    get_back_keyboard,
    get_cancel_keyboard,
    get_yes_no_keyboard,
)

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


class TestYesNoKeyboard:
    """Tests for yes/no keyboard."""

    def test_get_yes_no_keyboard(self) -> None:
        """Test yes/no keyboard creation."""
        keyboard = get_yes_no_keyboard()
        _assert_keyboard_has_buttons(keyboard, ["Да", "Нет"])


class TestBackKeyboard:
    """Tests for back keyboard."""

    def test_get_back_keyboard(self) -> None:
        """Test back keyboard creation."""
        keyboard = get_back_keyboard("back_to_menu")
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons


class TestCancelKeyboard:
    """Tests for cancel keyboard."""

    def test_get_cancel_keyboard(self) -> None:
        """Test cancel keyboard creation."""
        keyboard = get_cancel_keyboard()
        _assert_keyboard_has_buttons(keyboard, ["Отмена"])
