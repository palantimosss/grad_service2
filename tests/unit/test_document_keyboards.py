"""Tests for document keyboards."""

from bot.keyboards._documents import (
    get_document_type_keyboard,
    get_documents_keyboard,
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


# Mock class for tests
class MockDoc:
    """Mock document for tests."""

    def __init__(self, obj_id: int, file_name: str):
        self.id = obj_id
        self.file_name = file_name


class TestDocumentTypeKeyboard:
    """Tests for document type selection keyboard."""

    def test_get_document_type_keyboard(self) -> None:
        """Test document type keyboard creation."""
        keyboard = get_document_type_keyboard()
        buttons = _get_keyboard_buttons(keyboard)
        # Check for document type buttons (English or Russian)
        has_doc_type = any(
            doc_type in btn for doc_type in [
                "Source", "Исходный", "Work", "Result", "Other",
            ]
            for btn in buttons
        )
        assert has_doc_type or any(
            "source" in btn.lower() for btn in buttons
        )


class TestDocumentsKeyboard:
    """Tests for documents keyboard."""

    def test_get_documents_keyboard(self) -> None:
        """Test documents keyboard creation."""
        docs = [
            MockDoc(1, "doc1.pdf"),
            MockDoc(2, "doc2.pdf"),
        ]
        keyboard = get_documents_keyboard(docs, project_id=1)
        _assert_keyboard_has_buttons(
            keyboard, ["📄 doc1.pdf", "📄 doc2.pdf", _BACK_BUTTON],
        )
