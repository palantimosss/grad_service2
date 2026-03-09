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

# State attribute definitions (use tuples for immutability)
_USER_REG_ATTRS: tuple[str, ...] = (
    "role", "phone", "email", "position", "consent",
)
_PROFILE_EDIT_ATTRS: tuple[str, ...] = ("field", "value")
_PROJECT_CREATE_ATTRS: tuple[str, ...] = (
    "title", "description", "deadline", "budget",
)
_TASK_CREATE_ATTRS: tuple[str, ...] = (
    "title", "description", "performer", "deadline", "priority",
)
_STAGE_CREATE_ATTRS: tuple[str, ...] = (
    "title", "description", "planned_start", "planned_end", "order",
)
_MEETING_CREATE_ATTRS: tuple[str, ...] = (
    "title", "description", "scheduled_at", "duration",
    "format_type", "address", "online_link",
)
_DOC_UPLOAD_ATTRS: tuple[str, ...] = (
    "project", "task", "document_type", "description", "file",
)
_FEEDBACK_CREATE_ATTRS: tuple[str, ...] = ("project", "message", "rating")
_COMPANY_CREATE_ATTRS: tuple[str, ...] = (
    "name", "inn", "kpp", "address", "phone", "email", "website",
)


class TestUserStates:
    """Tests for user-related FSM states."""

    def test_user_registration_states(self) -> None:
        """Test UserRegistration states."""
        self._check_attrs(UserRegistration, _USER_REG_ATTRS)

    def test_profile_edit_states(self) -> None:
        """Test ProfileEdit states."""
        self._check_attrs(ProfileEdit, _PROFILE_EDIT_ATTRS)

    @staticmethod
    def _check_attrs(state_class: object, attrs: tuple[str, ...]) -> None:
        """Check state class has expected attributes."""
        for attr in attrs:
            assert hasattr(state_class, attr)


class TestProjectStates:
    """Tests for project-related FSM states."""

    def test_project_creation_states(self) -> None:
        """Test ProjectCreation states."""
        self._check_attrs(ProjectCreation, _PROJECT_CREATE_ATTRS)

    def test_task_creation_states(self) -> None:
        """Test TaskCreation states."""
        self._check_attrs(TaskCreation, _TASK_CREATE_ATTRS)

    def test_stage_creation_states(self) -> None:
        """Test StageCreation states."""
        self._check_attrs(StageCreation, _STAGE_CREATE_ATTRS)

    @staticmethod
    def _check_attrs(state_class: object, attrs: tuple[str, ...]) -> None:
        """Check state class has expected attributes."""
        for attr in attrs:
            assert hasattr(state_class, attr)


class TestOtherStates:
    """Tests for other FSM states."""

    def test_meeting_creation_states(self) -> None:
        """Test MeetingCreation states."""
        self._check_attrs(MeetingCreation, _MEETING_CREATE_ATTRS)

    def test_document_upload_states(self) -> None:
        """Test DocumentUpload states."""
        self._check_attrs(DocumentUpload, _DOC_UPLOAD_ATTRS)

    def test_feedback_creation_states(self) -> None:
        """Test FeedbackCreation states."""
        self._check_attrs(FeedbackCreation, _FEEDBACK_CREATE_ATTRS)

    def test_company_creation_states(self) -> None:
        """Test CompanyCreation states."""
        self._check_attrs(CompanyCreation, _COMPANY_CREATE_ATTRS)

    @staticmethod
    def _check_attrs(state_class: object, attrs: tuple[str, ...]) -> None:
        """Check state class has expected attributes."""
        for attr in attrs:
            assert hasattr(state_class, attr)
