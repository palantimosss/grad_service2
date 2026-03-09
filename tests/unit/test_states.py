"""Tests for FSM states."""

from bot.states.states import (
    CompanyCreation,
    DocumentUpload,
    FeedbackCreation,
    MeetingCreation,
    ProfileEdit,
    ProjectCreation,
    StageCreation,
    TaskCreation,
    UserRegistration,
)

# Common attribute names
_TITLE = "title"
_DESCRIPTION = "description"

# State attribute definitions (use tuples for immutability)
_USER_REG_ATTRS: tuple[str, ...] = (
    "role", "phone", "email", "position", "consent",
)
_PROFILE_EDIT_ATTRS: tuple[str, ...] = ("field", "value")
_PROJECT_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "deadline", "budget",
)
_TASK_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "performer", "deadline", "priority",
)
_STAGE_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "planned_start", "planned_end", "order",
)
_MEETING_CREATE_ATTRS: tuple[str, ...] = (
    _TITLE, _DESCRIPTION, "scheduled_at", "duration",
    "format_type", "address", "online_link",
)
_DOC_UPLOAD_ATTRS: tuple[str, ...] = (
    "project", "task", "document_type", _DESCRIPTION, "file",
)
_FEEDBACK_CREATE_ATTRS: tuple[str, ...] = ("project", "message", "rating")
_COMPANY_CREATE_ATTRS: tuple[str, ...] = (
    "name", "inn", "kpp", "address", "phone", "email", "website",
)


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


class TestOtherStates:
    """Tests for other FSM states."""

    def test_meeting_creation_states(self) -> None:
        """Test MeetingCreation states."""
        _check_attrs(MeetingCreation, _MEETING_CREATE_ATTRS)

    def test_document_upload_states(self) -> None:
        """Test DocumentUpload states."""
        _check_attrs(DocumentUpload, _DOC_UPLOAD_ATTRS)

    def test_feedback_creation_states(self) -> None:
        """Test FeedbackCreation states."""
        _check_attrs(FeedbackCreation, _FEEDBACK_CREATE_ATTRS)

    def test_company_creation_states(self) -> None:
        """Test CompanyCreation states."""
        _check_attrs(CompanyCreation, _COMPANY_CREATE_ATTRS)
