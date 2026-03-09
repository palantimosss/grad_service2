"""Tests for services module."""

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.config import (
    ADMIN_IDS,
    BASE_DIR,
    BOT_TOKEN,
    DATA_DIR,
    DATABASE_PATH,
    DEADLINE_MAX_HOURS,
    DEADLINE_MIN_HOURS,
    FILES_DIR,
    HOUR_SECONDS,
    YANDEX_GEOCODER_API_KEY,
)
from bot.database.crud_modules.meeting_crud import create_meeting
from bot.database.models.enums import DocumentType
from bot.middleware.logging import LoggingMiddleware
from bot.services.bot_factory import create_bot
from bot.services.calendar import (
    add_participant_service,
    cancel_meeting_service,
    complete_meeting_service,
    confirm_meeting_service,
    create_meeting_service,
)
from bot.services.dispatcher_factory import create_dispatcher
from bot.services.files import (
    create_document_service,
    delete_document_service,
    get_document_file,
)
from bot.services.routers import register_routers
from bot.services.scheduler import check_deadlines, create_scheduler
from bot.services.stage_service import create_stage_service
from bot.services.startup import on_shutdown, on_startup
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

# Constants for test assertions
EXPECTED_DEADLINE_MAX_HOURS = 25
EXPECTED_DEADLINE_MIN_HOURS = 23
EXPECTED_HOUR_SECONDS = 3600


@pytest.mark.asyncio
class TestBotFactory:
    """Tests for bot factory."""

    async def test_create_bot(self) -> None:
        """Test bot creation."""
        with patch("bot.services.bot_factory.Bot") as mock_bot:
            mock_bot_instance = MagicMock()
            mock_bot.return_value = mock_bot_instance
            bot = create_bot()
            assert bot is not None


class TestDispatcherFactory:
    """Tests for dispatcher factory."""

    def test_create_dispatcher(self) -> None:
        """Test dispatcher creation."""
        dispatcher = create_dispatcher()
        assert dispatcher is not None
        assert hasattr(dispatcher, "update")


class TestScheduler:
    """Tests for scheduler."""

    def test_create_scheduler(self) -> None:
        """Test scheduler creation."""
        scheduler = create_scheduler()
        assert scheduler is not None

    async def test_check_deadlines(self) -> None:
        """Test check deadlines function."""
        await check_deadlines()


@pytest.mark.asyncio
class TestStartup:
    """Tests for startup/shutdown hooks."""

    async def test_on_startup(self) -> None:
        """Test on_startup hook."""
        mock_bot = AsyncMock()
        mock_bot.get_me = AsyncMock(
            return_value=MagicMock(username="test_bot"),
        )

        with patch(
            "bot.services.startup.create_tables",
            new_callable=AsyncMock,
        ):
            await on_startup(mock_bot)
            mock_bot.get_me.assert_called_once()

    async def test_on_shutdown(self) -> None:
        """Test on_shutdown hook."""
        mock_bot = AsyncMock()
        mock_bot.session.close = AsyncMock()

        await on_shutdown(mock_bot)
        mock_bot.session.close.assert_called_once()


class TestRouters:
    """Tests for routers registration."""

    def test_register_routers(self) -> None:
        """Test routers registration."""
        mock_dispatcher = MagicMock()
        mock_dispatcher.include_routers = MagicMock()

        register_routers(mock_dispatcher)
        mock_dispatcher.include_routers.assert_called_once()


@pytest.mark.asyncio
class TestCalendarService:
    """Tests for calendar service."""

    async def test_create_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating meeting through service."""
        meeting = await create_meeting_service(
            session=test_session,
            params={
                "project_id": test_project.id,
                "title": "Service Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        assert meeting is not None

    async def test_confirm_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test confirming meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        confirmed = await confirm_meeting_service(test_session, meeting.id)
        assert confirmed is not None

    async def test_cancel_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test cancelling meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        cancelled = await cancel_meeting_service(test_session, meeting.id)
        assert cancelled is not None

    async def test_complete_meeting_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test completing meeting through service."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        completed = await complete_meeting_service(test_session, meeting.id)
        assert completed is not None

    async def test_add_participant_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test adding participant through service."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        participant = await add_participant_service(
            test_session,
            meeting.id,
            test_user.id,
        )
        assert participant is not None


class TestFilesService:
    """Tests for files service."""

    async def test_create_document_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating document through service."""
        doc = await create_document_service(
            session=test_session,
            project_id=test_project.id,
            file_path="/files/test.pdf",
            file_name="test.pdf",
            file_size=1024,
            document_type=DocumentType.SOURCE,
            uploaded_by=test_user.id,
        )
        assert doc is not None
        assert doc.file_name == "test.pdf"

    async def test_delete_document_service(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting document through service."""
        doc = await create_document_service(
            session=test_session,
            project_id=test_project.id,
            file_path="/files/test_delete.pdf",
            file_name="test_delete.pdf",
            file_size=1024,
            document_type=DocumentType.SOURCE,
            uploaded_by=test_user.id,
        )
        assert doc is not None

        with (
            patch("bot.services.files.os.path.exists", return_value=False),
            patch("bot.services.files.os.remove"),
        ):
            deleted = await delete_document_service(test_session, doc.id)
            assert deleted is True

    def test_get_document_file(self) -> None:
        """Test getting document file."""
        with patch("bot.services.files.FSInputFile") as mock_file:
            mock_file_instance = MagicMock()
            mock_file.return_value = mock_file_instance
            result = get_document_file("/path/to/file.pdf")
            assert result is not None


@pytest.mark.asyncio
class TestStageService:
    """Tests for stage service."""

    async def test_create_stage_service(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating stage through service."""
        stage = await create_stage_service(
            session=test_session,
            params={
                "project_id": test_project.id,
                "title": "Service Stage",
                "order": 1,
                "planned_start": datetime(2026, 1, 1, tzinfo=UTC),
                "planned_end": datetime(2026, 2, 1, tzinfo=UTC),
            },
        )
        assert stage is not None
        assert stage.title == "Service Stage"


class TestMiddleware:
    """Tests for middleware."""

    async def test_logging_middleware_message(self) -> None:
        """Test logging middleware with message."""
        middleware = LoggingMiddleware()
        mock_handler = AsyncMock(return_value="result")

        mock_message = MagicMock()
        mock_message.text = "Test message"
        mock_message.from_user.username = "testuser"

        data: dict = {}

        result = await middleware(mock_handler, mock_message, data)
        assert result == "result"

    async def test_logging_middleware_callback(self) -> None:
        """Test logging middleware with callback."""
        middleware = LoggingMiddleware()
        mock_handler = AsyncMock(return_value="result")

        mock_callback = MagicMock()
        mock_callback.data = "callback_data"
        mock_callback.from_user.username = "testuser"

        data: dict = {}

        result = await middleware(mock_handler, mock_callback, data)
        assert result == "result"


class TestStates:
    """Tests for FSM states."""

    def test_user_registration_states(self) -> None:
        """Test UserRegistration states."""
        assert hasattr(UserRegistration, "role")
        assert hasattr(UserRegistration, "phone")
        assert hasattr(UserRegistration, "email")
        assert hasattr(UserRegistration, "position")
        assert hasattr(UserRegistration, "consent")

    def test_profile_edit_states(self) -> None:
        """Test ProfileEdit states."""
        assert hasattr(ProfileEdit, "field")
        assert hasattr(ProfileEdit, "value")

    def test_project_creation_states(self) -> None:
        """Test ProjectCreation states."""
        assert hasattr(ProjectCreation, "title")
        assert hasattr(ProjectCreation, "description")
        assert hasattr(ProjectCreation, "deadline")
        assert hasattr(ProjectCreation, "budget")

    def test_task_creation_states(self) -> None:
        """Test TaskCreation states."""
        assert hasattr(TaskCreation, "title")
        assert hasattr(TaskCreation, "description")
        assert hasattr(TaskCreation, "performer")
        assert hasattr(TaskCreation, "deadline")
        assert hasattr(TaskCreation, "priority")

    def test_stage_creation_states(self) -> None:
        """Test StageCreation states."""
        assert hasattr(StageCreation, "title")
        assert hasattr(StageCreation, "description")
        assert hasattr(StageCreation, "planned_start")
        assert hasattr(StageCreation, "planned_end")
        assert hasattr(StageCreation, "order")

    def test_meeting_creation_states(self) -> None:
        """Test MeetingCreation states."""
        assert hasattr(MeetingCreation, "title")
        assert hasattr(MeetingCreation, "description")
        assert hasattr(MeetingCreation, "scheduled_at")
        assert hasattr(MeetingCreation, "duration")
        assert hasattr(MeetingCreation, "format_type")
        assert hasattr(MeetingCreation, "address")
        assert hasattr(MeetingCreation, "online_link")

    def test_document_upload_states(self) -> None:
        """Test DocumentUpload states."""
        assert hasattr(DocumentUpload, "project")
        assert hasattr(DocumentUpload, "task")
        assert hasattr(DocumentUpload, "document_type")
        assert hasattr(DocumentUpload, "description")
        assert hasattr(DocumentUpload, "file")

    def test_feedback_creation_states(self) -> None:
        """Test FeedbackCreation states."""
        assert hasattr(FeedbackCreation, "project")
        assert hasattr(FeedbackCreation, "message")
        assert hasattr(FeedbackCreation, "rating")

    def test_company_creation_states(self) -> None:
        """Test CompanyCreation states."""
        assert hasattr(CompanyCreation, "name")
        assert hasattr(CompanyCreation, "inn")
        assert hasattr(CompanyCreation, "kpp")
        assert hasattr(CompanyCreation, "address")
        assert hasattr(CompanyCreation, "phone")
        assert hasattr(CompanyCreation, "email")
        assert hasattr(CompanyCreation, "website")


class TestConfig:
    """Tests for config module."""

    def test_config_constants(self) -> None:
        """Test config constants."""
        assert HOUR_SECONDS == EXPECTED_HOUR_SECONDS
        assert DEADLINE_MIN_HOURS == EXPECTED_DEADLINE_MIN_HOURS
        assert DEADLINE_MAX_HOURS == EXPECTED_DEADLINE_MAX_HOURS
        assert BASE_DIR is not None
        assert DATA_DIR is not None
        assert DATABASE_PATH is not None
        assert FILES_DIR is not None

    def test_bot_token(self) -> None:
        """Test bot token config."""
        assert isinstance(BOT_TOKEN, str)

    def test_admin_ids(self) -> None:
        """Test admin IDs config."""
        assert isinstance(ADMIN_IDS, list)

    def test_yandex_geocoder_api_key(self) -> None:
        """Test Yandex Geocoder API key config."""
        assert isinstance(YANDEX_GEOCODER_API_KEY, str)
