"""Tests for keyboards/menus module."""

from bot.database.models.enums import TaskStatus, UserRole
from bot.keyboards.menus import (
    get_back_keyboard,
    get_cancel_keyboard,
    get_clients_keyboard,
    get_document_type_keyboard,
    get_documents_keyboard,
    get_edit_profile_keyboard,
    get_main_menu_keyboard,
    get_meeting_response_keyboard,
    get_notification_keyboard,
    get_profile_keyboard,
    get_project_actions_keyboard,
    get_project_status_keyboard,
    get_projects_keyboard,
    get_role_keyboard,
    get_task_actions_keyboard,
    get_tasks_keyboard,
    get_yes_no_keyboard,
)

# Constants for test assertions
EXPECTED_THREE_ROWS = 3
_BACK_BUTTON = "Назад"
_UPLOAD_DOC_BUTTON = "Загрузить документ"


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


# Mock classes for tests
class MockProject:
    """Mock project for tests."""

    def __init__(self, obj_id: int, title: str):
        self.id = obj_id
        self.title = title


class MockTask:
    """Mock task for tests."""

    def __init__(self, obj_id: int, title: str, status: TaskStatus):
        self.id = obj_id
        self.title = title
        self.status = status


class MockDoc:
    """Mock document for tests."""

    def __init__(self, obj_id: int, file_name: str):
        self.id = obj_id
        self.file_name = file_name


class MockCompany:
    """Mock company for tests."""

    def __init__(self, obj_id: int, name: str):
        self.id = obj_id
        self.name = name


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


class TestProjectsKeyboard:
    """Tests for projects keyboard."""

    def test_get_projects_keyboard_empty(self) -> None:
        """Test projects keyboard with empty list."""
        keyboard = get_projects_keyboard([])
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons

    def test_get_projects_keyboard_with_projects(self) -> None:
        """Test projects keyboard with projects list."""
        projects = [
            MockProject(1, "Project 1"),
            MockProject(2, "Project 2"),
        ]
        keyboard = get_projects_keyboard(projects)
        _assert_keyboard_has_buttons(
            keyboard, ["📁 Project 1", "📁 Project 2", _BACK_BUTTON],
        )


class TestProjectActionsKeyboard:
    """Tests for project actions keyboard."""

    def test_get_project_actions_keyboard_client(self) -> None:
        """Test project actions keyboard for client."""
        keyboard = get_project_actions_keyboard(1, UserRole.CLIENT)
        _assert_keyboard_has_buttons(
            keyboard, [_UPLOAD_DOC_BUTTON, "Обратная связь"],
        )

    def test_get_project_actions_keyboard_manager(self) -> None:
        """Test project actions keyboard for manager."""
        keyboard = get_project_actions_keyboard(1, UserRole.MANAGER)
        _assert_keyboard_has_buttons(
            keyboard, ["Создать задачу", "Создать этап", "Создать встречу"],
        )

    def test_get_project_actions_keyboard_performer(self) -> None:
        """Test project actions keyboard for performer."""
        keyboard = get_project_actions_keyboard(1, UserRole.PERFORMER)
        buttons = _get_keyboard_buttons(keyboard)
        assert _UPLOAD_DOC_BUTTON in buttons


class TestTasksKeyboard:
    """Tests for tasks keyboard."""

    def test_get_tasks_keyboard_empty(self) -> None:
        """Test tasks keyboard with empty list."""
        keyboard = get_tasks_keyboard([])
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons

    def test_get_tasks_keyboard_with_tasks(self) -> None:
        """Test tasks keyboard with tasks list."""
        tasks = [
            MockTask(1, "Task 1", TaskStatus.PENDING),
            MockTask(2, "Task 2", TaskStatus.COMPLETED),
        ]
        keyboard = get_tasks_keyboard(tasks)
        _assert_keyboard_has_buttons(
            keyboard, ["⏳ Task 1", "✅ Task 2", _BACK_BUTTON],
        )


class TestDocumentTypeKeyboard:
    """Tests for document type selection keyboard."""

    def test_get_document_type_keyboard(self) -> None:
        """Test document type keyboard creation."""
        keyboard = get_document_type_keyboard()
        buttons = _get_keyboard_buttons(keyboard)
        # Check for document type buttons (English or Russian)
        has_doc_type = any(
            t in b for t in ["Source", "Исходный", "Work", "Result", "Other"]
            for b in buttons
        )
        assert has_doc_type or any("source" in b.lower() for b in buttons)


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


class TestMeetingResponseKeyboard:
    """Tests for meeting response keyboard."""

    def test_get_meeting_response_keyboard(self) -> None:
        """Test meeting response keyboard creation."""
        keyboard = get_meeting_response_keyboard(1)
        _assert_keyboard_has_buttons(keyboard, ["Подтвердить", "Отклонить"])


class TestTaskActionsKeyboard:
    """Tests for task actions keyboard."""

    def test_get_task_actions_keyboard_pending(self) -> None:
        """Test task actions keyboard for pending task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.PENDING)
        _assert_keyboard_has_buttons(
            keyboard, ["Взять в работу", _UPLOAD_DOC_BUTTON],
        )

    def test_get_task_actions_keyboard_in_progress(self) -> None:
        """Test task actions keyboard for in_progress task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.IN_PROGRESS)
        _assert_keyboard_has_buttons(
            keyboard, ["Завершить", _UPLOAD_DOC_BUTTON],
        )


class TestProjectStatusKeyboard:
    """Tests for project status keyboard."""

    def test_get_project_status_keyboard(self) -> None:
        """Test project status keyboard creation."""
        keyboard = get_project_status_keyboard(1)
        buttons = _get_keyboard_buttons(keyboard)
        assert _BACK_BUTTON in buttons
        assert len(buttons) > 1  # At least some status buttons


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


class TestCancelKeyboard:
    """Tests for cancel keyboard."""

    def test_get_cancel_keyboard(self) -> None:
        """Test cancel keyboard creation."""
        keyboard = get_cancel_keyboard()
        _assert_keyboard_has_buttons(keyboard, ["Отмена"])


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
