"""Tests for FSM states - user states."""

from bot.states.states import (
    ProfileEdit,
    UserRegistration,
)

# State attribute definitions (use tuples for immutability)
_USER_REG_ATTRS: tuple[str, ...] = (
    "role", "phone", "email", "position", "consent",
)
_PROFILE_EDIT_ATTRS: tuple[str, ...] = ("field", "value")


def _check_attrs(state_class: object, attrs: tuple[str, ...]) -> None:
    """Check state class has expected attributes."""
    for attr in attrs:
        assert hasattr(state_class, attr)


class TestUserStates:
    """Tests for user-related FSM states."""

    def test_user_registration_states(self) -> None:
        """Test UserRegistration states."""
        _check_attrs(UserRegistration, _USER_REG_ATTRS)

    def test_profile_edit_states(self) -> None:
        """Test ProfileEdit states."""
        _check_attrs(ProfileEdit, _PROFILE_EDIT_ATTRS)
