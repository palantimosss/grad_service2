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


class TestStates:
    """Tests for FSM states."""

    def _assert_state_has_attributes(
        self, state_class: object, attributes: list[str],
    ) -> None:
        """Assert state class has expected attributes."""
        for attr in attributes:
            assert hasattr(state_class, attr)

    def test_user_registration_states(self) -> None:
        """Test UserRegistration states."""
        self._assert_state_has_attributes(
            UserRegistration,
            ["role", "phone", "email", "position", "consent"],
        )

    def test_profile_edit_states(self) -> None:
        """Test ProfileEdit states."""
        self._assert_state_has_attributes(
            ProfileEdit, ["field", "value"],
        )

    def test_project_creation_states(self) -> None:
        """Test ProjectCreation states."""
        self._assert_state_has_attributes(
            ProjectCreation, ["title", "description", "deadline", "budget"],
        )

    def test_task_creation_states(self) -> None:
        """Test TaskCreation states."""
        self._assert_state_has_attributes(
            TaskCreation,
            ["title", "description", "performer", "deadline", "priority"],
        )

    def test_stage_creation_states(self) -> None:
        """Test StageCreation states."""
        self._assert_state_has_attributes(
            StageCreation,
            ["title", "description", "planned_start", "planned_end", "order"],
        )

    def test_meeting_creation_states(self) -> None:
        """Test MeetingCreation states."""
        self._assert_state_has_attributes(
            MeetingCreation,
            [
                "title", "description", "scheduled_at", "duration",
                "format_type", "address", "online_link",
            ],
        )

    def test_document_upload_states(self) -> None:
        """Test DocumentUpload states."""
        self._assert_state_has_attributes(
            DocumentUpload,
            ["project", "task", "document_type", "description", "file"],
        )

    def test_feedback_creation_states(self) -> None:
        """Test FeedbackCreation states."""
        self._assert_state_has_attributes(
            FeedbackCreation, ["project", "message", "rating"],
        )

    def test_company_creation_states(self) -> None:
        """Test CompanyCreation states."""
        self._assert_state_has_attributes(
            CompanyCreation,
            ["name", "inn", "kpp", "address", "phone", "email", "website"],
        )
