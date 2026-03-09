"""Tests for profile keyboards: role, main menu, profile, edit profile."""

from bot.database.models.enums import UserRole
from bot.keyboards._profile import (
    get_edit_profile_keyboard,
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_role_keyboard,
)

# Constants for test assertions
EXPECTED_THREE_ROWS = 3
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


class TestRoleKeyboard:
    """Tests for role selection keyboard."""

    def test_get_role_keyboard(self) -> None:
        """Test role keyboard creation."""
        keyboard = get_role_keyboard()
        assert len(keyboard.inline_keyboard) == EXPECTED_THREE_ROWS


class TestMainMenuKeyboard:
    """Tests for main menu keyboard."""

    def test_get_main_menu_keyboard_client(self) -> None:
        """Test main menu keyboard for client role."""
        keyboard = get_main_menu_keyboard(UserRole.CLIENT)
        _assert_keyboard_has_buttons(
            keyboard, ["Мои проекты", "Создать проект", "Профиль"],
        )

    def test_get_main_menu_keyboard_manager(self) -> None:
        """Test main menu keyboard for manager role."""
        keyboard = get_main_menu_keyboard(UserRole.MANAGER)
        _assert_keyboard_has_buttons(
            keyboard,
            [
                "Все проекты",
                "Заявки",
                "Задачи",
                "Клиенты",
                "Статистика",
                "Профиль",
            ],
        )

    def test_get_main_menu_keyboard_performer(self) -> None:
        """Test main menu keyboard for performer role."""
        keyboard = get_main_menu_keyboard(UserRole.PERFORMER)
        _assert_keyboard_has_buttons(
            keyboard, ["Мои задачи", "Проекты", "Профиль"],
        )


class TestProfileKeyboard:
    """Tests for profile keyboard."""

    def test_get_profile_keyboard(self) -> None:
        """Test profile keyboard creation."""
        keyboard = get_profile_keyboard()
        _assert_keyboard_has_buttons(keyboard, ["Редактировать", _BACK_BUTTON])


class TestEditProfileKeyboard:
    """Tests for edit profile keyboard."""

    def test_get_edit_profile_keyboard(self) -> None:
        """Test edit profile keyboard creation."""
        keyboard = get_edit_profile_keyboard()
        _assert_keyboard_has_buttons(
            keyboard, ["Телефон", "Email", "Должность", _BACK_BUTTON],
        )
