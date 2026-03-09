"""Tests for FSM states - other states."""

from bot.states.states import (
    CompanyCreation,
    DocumentUpload,
    FeedbackCreation,
    MeetingCreation,
)

# Common attribute names
_TITLE = "title"
_DESCRIPTION = "description"

# State attribute definitions (use tuples for immutability)
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
