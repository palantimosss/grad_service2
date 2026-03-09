"""Tests for FSM states - project states."""

from bot.states.states import (
    ProjectCreation,
    StageCreation,
    TaskCreation,
)

# Common attribute names
_TITLE = "title"
_DESCRIPTION = "description"

# State attribute definitions (use tuples for immutability)
_PROJECT_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "deadline", "budget",
)
_TASK_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "performer", "deadline", "priority",
)
_STAGE_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "planned_start", "planned_end", "order",
)


def _check_attrs(state_class: object, attrs: tuple[str, ...]) -> None:
    """Check state class has expected attributes."""
    for attr in attrs:
        assert hasattr(state_class, attr)


class TestProjectStates:
    """Tests for project-related FSM states."""

    def test_project_creation_states(self) -> None:
        """Test ProjectCreation states."""
        _check_attrs(ProjectCreation, _PROJECT_CREATE_ATTRS)

    def test_task_creation_states(self) -> None:
        """Test TaskCreation states."""
        _check_attrs(TaskCreation, _TASK_CREATE_ATTRS)

    def test_stage_creation_states(self) -> None:
        """Test StageCreation states."""
        _check_attrs(StageCreation, _STAGE_CREATE_ATTRS)
