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


class TestRoleKeyboard:
    """Tests for role selection keyboard."""

    def test_get_role_keyboard(self) -> None:
        """Test role keyboard creation."""
        keyboard = get_role_keyboard()
        assert keyboard is not None
        assert len(keyboard.inline_keyboard) == EXPECTED_THREE_ROWS


class TestMainMenuKeyboard:
    """Tests for main menu keyboard."""

    def test_get_main_menu_keyboard_client(self) -> None:
        """Test main menu keyboard for client role."""
        keyboard = get_main_menu_keyboard(UserRole.CLIENT)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Мои проекты" in buttons
        assert "Создать проект" in buttons
        assert "Профиль" in buttons

    def test_get_main_menu_keyboard_manager(self) -> None:
        """Test main menu keyboard for manager role."""
        keyboard = get_main_menu_keyboard(UserRole.MANAGER)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Все проекты" in buttons
        assert "Заявки" in buttons
        assert "Задачи" in buttons
        assert "Клиенты" in buttons
        assert "Статистика" in buttons
        assert "Профиль" in buttons

    def test_get_main_menu_keyboard_performer(self) -> None:
        """Test main menu keyboard for performer role."""
        keyboard = get_main_menu_keyboard(UserRole.PERFORMER)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Мои задачи" in buttons
        assert "Проекты" in buttons
        assert "Профиль" in buttons


class TestProfileKeyboard:
    """Tests for profile keyboard."""

    def test_get_profile_keyboard(self) -> None:
        """Test profile keyboard creation."""
        keyboard = get_profile_keyboard()
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Редактировать" in buttons
        assert "Назад" in buttons


class TestEditProfileKeyboard:
    """Tests for edit profile keyboard."""

    def test_get_edit_profile_keyboard(self) -> None:
        """Test edit profile keyboard creation."""
        keyboard = get_edit_profile_keyboard()
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Телефон" in buttons
        assert "Email" in buttons
        assert "Должность" in buttons
        assert "Назад" in buttons


class TestProjectsKeyboard:
    """Tests for projects keyboard."""

    def test_get_projects_keyboard_empty(self) -> None:
        """Test projects keyboard with empty list."""
        keyboard = get_projects_keyboard([])
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Назад" in buttons

    def test_get_projects_keyboard_with_projects(self) -> None:
        """Test projects keyboard with projects list."""

        class MockProject:
            def __init__(self, obj_id: int, title: str):
                self.id = obj_id
                self.title = title

        projects = [
            MockProject(1, "Project 1"),
            MockProject(2, "Project 2"),
        ]
        keyboard = get_projects_keyboard(projects)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "📁 Project 1" in buttons
        assert "📁 Project 2" in buttons
        assert "Назад" in buttons


class TestProjectActionsKeyboard:
    """Tests for project actions keyboard."""

    def test_get_project_actions_keyboard_client(self) -> None:
        """Test project actions keyboard for client."""
        keyboard = get_project_actions_keyboard(1, UserRole.CLIENT)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Загрузить документ" in buttons
        assert "Обратная связь" in buttons

    def test_get_project_actions_keyboard_manager(self) -> None:
        """Test project actions keyboard for manager."""
        keyboard = get_project_actions_keyboard(1, UserRole.MANAGER)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Создать задачу" in buttons
        assert "Создать этап" in buttons
        assert "Создать встречу" in buttons

    def test_get_project_actions_keyboard_performer(self) -> None:
        """Test project actions keyboard for performer."""
        keyboard = get_project_actions_keyboard(1, UserRole.PERFORMER)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Загрузить документ" in buttons


class TestTasksKeyboard:
    """Tests for tasks keyboard."""

    def test_get_tasks_keyboard_empty(self) -> None:
        """Test tasks keyboard with empty list."""
        keyboard = get_tasks_keyboard([])
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Назад" in buttons

    def test_get_tasks_keyboard_with_tasks(self) -> None:
        """Test tasks keyboard with tasks list."""

        class MockTask:
            def __init__(self, obj_id: int, title: str, status: TaskStatus):
                self.id = obj_id
                self.title = title
                self.status = status

        tasks = [
            MockTask(1, "Task 1", TaskStatus.PENDING),
            MockTask(2, "Task 2", TaskStatus.COMPLETED),
        ]
        keyboard = get_tasks_keyboard(tasks)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "⏳ Task 1" in buttons
        assert "✅ Task 2" in buttons
        assert "Назад" in buttons


class TestDocumentTypeKeyboard:
    """Tests for document type selection keyboard."""

    def test_get_document_type_keyboard(self) -> None:
        """Test document type keyboard creation."""
        keyboard = get_document_type_keyboard()
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
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
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Да" in buttons
        assert "Нет" in buttons


class TestBackKeyboard:
    """Tests for back keyboard."""

    def test_get_back_keyboard(self) -> None:
        """Test back keyboard creation."""
        keyboard = get_back_keyboard("back_to_menu")
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Назад" in buttons


class TestMeetingResponseKeyboard:
    """Tests for meeting response keyboard."""

    def test_get_meeting_response_keyboard(self) -> None:
        """Test meeting response keyboard creation."""
        keyboard = get_meeting_response_keyboard(1)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Подтвердить" in buttons
        assert "Отклонить" in buttons


class TestTaskActionsKeyboard:
    """Tests for task actions keyboard."""

    def test_get_task_actions_keyboard_pending(self) -> None:
        """Test task actions keyboard for pending task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.PENDING)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Взять в работу" in buttons
        assert "Загрузить документ" in buttons

    def test_get_task_actions_keyboard_in_progress(self) -> None:
        """Test task actions keyboard for in_progress task."""
        keyboard = get_task_actions_keyboard(1, TaskStatus.IN_PROGRESS)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Завершить" in buttons
        assert "Загрузить документ" in buttons


class TestProjectStatusKeyboard:
    """Tests for project status keyboard."""

    def test_get_project_status_keyboard(self) -> None:
        """Test project status keyboard creation."""
        keyboard = get_project_status_keyboard(1)
        assert keyboard is not None
        # Should have status buttons and back button
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Назад" in buttons
        assert len(buttons) > 1  # At least some status buttons


class TestDocumentsKeyboard:
    """Tests for documents keyboard."""

    def test_get_documents_keyboard(self) -> None:
        """Test documents keyboard creation."""

        class MockDoc:
            def __init__(self, obj_id: int, file_name: str):
                self.id = obj_id
                self.file_name = file_name

        docs = [
            MockDoc(1, "doc1.pdf"),
            MockDoc(2, "doc2.pdf"),
        ]
        keyboard = get_documents_keyboard(docs, project_id=1)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "📄 doc1.pdf" in buttons
        assert "📄 doc2.pdf" in buttons
        assert "Назад" in buttons


class TestCancelKeyboard:
    """Tests for cancel keyboard."""

    def test_get_cancel_keyboard(self) -> None:
        """Test cancel keyboard creation."""
        keyboard = get_cancel_keyboard()
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Отмена" in buttons


class TestClientsKeyboard:
    """Tests for clients keyboard."""

    def test_get_clients_keyboard(self) -> None:
        """Test clients keyboard creation."""

        class MockCompany:
            def __init__(self, obj_id: int, name: str):
                self.id = obj_id
                self.name = name

        companies = [
            MockCompany(1, "Company 1"),
            MockCompany(2, "Company 2"),
        ]
        keyboard = get_clients_keyboard(companies)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "🏢 Company 1" in buttons
        assert "🏢 Company 2" in buttons
        assert "Добавить клиента" in buttons
        assert "Назад" in buttons


class TestNotificationKeyboard:
    """Tests for notification keyboard."""

    def test_get_notification_keyboard(self) -> None:
        """Test notification keyboard creation."""
        keyboard = get_notification_keyboard(1)
        assert keyboard is not None
        buttons = [
            button.text for row in keyboard.inline_keyboard for button in row
        ]
        assert "Отметить прочитанным" in buttons
        assert "Назад" in buttons
