"""Extended unit tests for CRUD operations."""

import secrets
from datetime import UTC, datetime
from typing import TYPE_CHECKING

import pytest

from bot.database.crud_modules.client_company_crud import (
    create_company,
    delete_company,
    get_all_companies,
    get_company_by_id,
    update_company,
)
from bot.database.crud_modules.document_crud import (
    create_document,
    delete_document,
    get_document_by_id,
    get_documents_by_project_id,
    update_document,
)
from bot.database.crud_modules.feedback_crud import (
    create_feedback,
    delete_feedback,
    get_feedback_by_id,
    get_feedbacks_by_project_id,
)
from bot.database.crud_modules.gis_log_crud import (
    create_gis_check_log,
    delete_gis_log,
    get_gis_logs_by_meeting_id,
)
from bot.database.crud_modules.meeting_crud import (
    add_meeting_participant,
    create_meeting,
    delete_meeting,
    get_meeting_by_id,
    get_meetings_by_project_id,
    update_meeting_status,
    update_participant_status,
)
from bot.database.crud_modules.project_crud import create_project
from bot.database.crud_modules.stage_crud import (
    create_stage,
    delete_stage,
    get_stage_by_id,
    get_stages_by_project_id,
    update_stage_status,
)
from bot.database.crud_modules.statistics_crud import (
    get_manager_projects_count,
    get_performer_tasks_count,
    get_projects_count_by_status,
    get_tasks_count_by_status,
    get_total_projects_count,
    get_total_tasks_count,
    get_total_users_count,
    get_users_count_by_role,
)
from bot.database.crud_modules.task_crud import create_task
from bot.database.crud_modules.user_crud import create_user
from bot.database.models.enums import (
    DocumentType,
    MeetingParticipantStatus,
    MeetingStatus,
    ProjectStatus,
    TaskStatus,
    UserRole,
)

if TYPE_CHECKING:
    from bot.database.models.project import Project
    from bot.database.models.task import Task
    from bot.database.models.user import User

# Test constants
TEST_YEAR = 2026
TEST_MONTH = 12
TEST_DAY = 31
TEST_HOUR = 10
TEST_MINUTE = 0
TEST_MINUTE_LATER = 11
TEST_FILE_PATH = "/files/test.pdf"
TEST_FILE_NAME = "test.pdf"
TEST_FILE_SIZE = 1024
TEST_MEETING_TITLE = "Test Meeting"
TEST_COMPANY_NAME = "Test Company"
TEST_FEEDBACK_MESSAGE = "Great project!"
TEST_STAGE_TITLE = "Design Phase"
TEST_TELEGRAM_ID_MIN = 1_000_000_000
TEST_TELEGRAM_ID_MAX = 9_000_000_000

# Field key constants
_PROJECT_ID_KEY = "project_id"
_FILE_PATH_KEY = "file_path"
_FILE_NAME_KEY = "file_name"
_FILE_SIZE_KEY = "file_size"
_DOCUMENT_TYPE_KEY = "document_type"
_TITLE_KEY = "title"
_ORGANIZER_ID_KEY = "organizer_id"
_SCHEDULED_AT_KEY = "scheduled_at"
_AUTHOR_ID_KEY = "author_id"
_MESSAGE_KEY = "message"
_RATING_KEY = "rating"
_ORDER_KEY = "order"
_PLANNED_START_KEY = "planned_start"
_PLANNED_END_KEY = "planned_end"
_STATUS_KEY = "status"
_NAME_KEY = "name"
_MEETING_ID_KEY = "meeting_id"
_ADDRESS_KEY = "address"
_COORDINATES_KEY = "coordinates"
_INSIDE_ZONE_KEY = "inside_zone"

# Constants for test assertions
EXPECTED_ONE_ITEM = 1
EXPECTED_TWO_ITEMS = 2
EXPECTED_FIVE_RATING = 5


@pytest.mark.asyncio
class TestDocumentCRUD:
    """Tests for document CRUD operations."""

    async def test_create_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating document."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: TEST_FILE_PATH,
                _FILE_NAME_KEY: TEST_FILE_NAME,
                _FILE_SIZE_KEY: TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        assert doc.file_name == TEST_FILE_NAME
        assert doc.document_type == DocumentType.SOURCE

    async def test_get_document_by_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting document by ID."""
        doc = await create_document(
            test_session,
            {
                "project_id": test_project.id,
                "file_path": "/files/test.pdf",
                "file_name": "test.pdf",
                "file_size": 1024,
                "document_type": DocumentType.SOURCE,
            },
        )
        retrieved = await get_document_by_id(test_session, doc.id)
        assert retrieved is not None
        assert retrieved.file_name == "test.pdf"

    async def test_get_documents_by_project_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting documents by project ID."""
        await create_document(
            test_session,
            {
                "project_id": test_project.id,
                "file_path": "/files/test1.pdf",
                "file_name": "test1.pdf",
                "file_size": 1024,
                "document_type": DocumentType.SOURCE,
            },
        )
        await create_document(
            test_session,
            {
                "project_id": test_project.id,
                "file_path": "/files/test2.pdf",
                "file_name": "test2.pdf",
                "file_size": 2048,
                "document_type": DocumentType.WORK,
            },
        )
        docs = await get_documents_by_project_id(test_session, test_project.id)
        assert len(docs) == EXPECTED_TWO_ITEMS

    async def test_update_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test updating document."""
        doc = await create_document(
            test_session,
            {
                "project_id": test_project.id,
                "file_path": "/files/test.pdf",
                "file_name": "test.pdf",
                "file_size": 1024,
                "document_type": DocumentType.SOURCE,
            },
        )
        updated = await update_document(
            test_session,
            doc.id,
            {"file_name": "updated.pdf", "description": "Updated doc"},
        )
        assert updated is not None
        assert updated.file_name == "updated.pdf"

    async def test_delete_document(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test deleting document."""
        doc = await create_document(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _FILE_PATH_KEY: TEST_FILE_PATH,
                _FILE_NAME_KEY: TEST_FILE_NAME,
                _FILE_SIZE_KEY: TEST_FILE_SIZE,
                _DOCUMENT_TYPE_KEY: DocumentType.SOURCE,
            },
        )
        deleted = await delete_document(test_session, doc.id)
        assert deleted is True
        retrieved = await get_document_by_id(test_session, doc.id)
        assert retrieved is None


@pytest.mark.asyncio
class TestMeetingCRUD:
    """Tests for meeting CRUD operations."""

    async def test_create_meeting(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating meeting."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_HOUR, TEST_MINUTE, tzinfo=UTC,
                ),
                "duration_minutes": 60,
                "is_online": True,
            },
        )
        assert meeting.title == TEST_MEETING_TITLE
        assert meeting.is_online is True

    async def test_get_meeting_by_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting meeting by ID."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_HOUR, TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        retrieved = await get_meeting_by_id(test_session, meeting.id)
        assert retrieved is not None
        assert retrieved.title == TEST_MEETING_TITLE

    async def test_get_meetings_by_project_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting meetings by project ID."""
        await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Meeting 1",
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_HOUR, TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Meeting 2",
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_MINUTE_LATER, TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        meetings = await get_meetings_by_project_id(
            test_session, test_project.id,
        )
        assert len(meetings) == EXPECTED_TWO_ITEMS

    async def test_update_meeting_status(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test updating meeting status."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        updated = await update_meeting_status(
            test_session,
            meeting.id,
            MeetingStatus.CONFIRMED,
        )
        assert updated is not None
        assert updated.status == MeetingStatus.CONFIRMED

    async def test_delete_meeting(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting meeting."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        deleted = await delete_meeting(test_session, meeting.id)
        assert deleted is True
        retrieved = await get_meeting_by_id(test_session, meeting.id)
        assert retrieved is None

    async def test_add_meeting_participant(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test adding participant to meeting."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        participant = await add_meeting_participant(
            test_session,
            meeting.id,
            test_user.id,
        )
        assert participant.meeting_id == meeting.id
        assert participant.user_id == test_user.id
        assert participant.status == MeetingParticipantStatus.PENDING

    async def test_update_participant_status(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test updating participant status."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        await add_meeting_participant(
            test_session,
            meeting.id,
            test_user.id,
        )
        participant = await update_participant_status(
            test_session,
            meeting.id,
            test_user.id,
            MeetingParticipantStatus.CONFIRMED,
        )
        assert participant is not None
        assert participant.status == MeetingParticipantStatus.CONFIRMED


@pytest.mark.asyncio
class TestFeedbackCRUD:
    """Tests for feedback CRUD operations."""

    async def test_create_feedback(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating feedback."""
        feedback = await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: TEST_FEEDBACK_MESSAGE,
                _RATING_KEY: EXPECTED_FIVE_RATING,
            },
        )
        assert feedback.message == TEST_FEEDBACK_MESSAGE
        assert feedback.rating == EXPECTED_FIVE_RATING

    async def test_get_feedback_by_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting feedback by ID."""
        feedback = await create_feedback(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _AUTHOR_ID_KEY: test_user.id,
                _MESSAGE_KEY: TEST_FEEDBACK_MESSAGE,
                _RATING_KEY: EXPECTED_FIVE_RATING,
            },
        )
        retrieved = await get_feedback_by_id(test_session, feedback.id)
        assert retrieved is not None
        assert retrieved.message == TEST_FEEDBACK_MESSAGE

    async def test_get_feedbacks_by_project_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting feedbacks by project ID."""
        await create_feedback(
            test_session,
            {
                "project_id": test_project.id,
                "author_id": test_user.id,
                "message": "Feedback 1",
                "rating": 4,
            },
        )
        await create_feedback(
            test_session,
            {
                "project_id": test_project.id,
                "author_id": test_user.id,
                "message": "Feedback 2",
                "rating": 5,
            },
        )
        feedbacks = await get_feedbacks_by_project_id(
            test_session, test_project.id,
        )
        assert len(feedbacks) == EXPECTED_TWO_ITEMS

    async def test_delete_feedback(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting feedback."""
        feedback = await create_feedback(
            test_session,
            {
                "project_id": test_project.id,
                "author_id": test_user.id,
                "message": "Great project!",
                "rating": 5,
            },
        )
        deleted = await delete_feedback(test_session, feedback.id)
        assert deleted is True
        retrieved = await get_feedback_by_id(test_session, feedback.id)
        assert retrieved is None


@pytest.mark.asyncio
class TestStageCRUD:
    """Tests for stage CRUD operations."""

    async def test_create_stage(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test creating stage."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(TEST_YEAR, 1, 1, tzinfo=UTC),
                _PLANNED_END_KEY: datetime(TEST_YEAR, 2, 1, tzinfo=UTC),
            },
        )
        assert stage.title == TEST_STAGE_TITLE
        assert stage.order == 1

    async def test_get_stage_by_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting stage by ID."""
        stage = await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_STAGE_TITLE,
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(TEST_YEAR, 1, 1, tzinfo=UTC),
                _PLANNED_END_KEY: datetime(TEST_YEAR, 2, 1, tzinfo=UTC),
            },
        )
        retrieved = await get_stage_by_id(test_session, stage.id)
        assert retrieved is not None
        assert retrieved.title == TEST_STAGE_TITLE

    async def test_get_stages_by_project_id(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting stages by project ID."""
        await create_stage(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: "Stage 1",
                _ORDER_KEY: 1,
                _PLANNED_START_KEY: datetime(TEST_YEAR, 1, 1, tzinfo=UTC),
            },
        )
        await create_stage(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Stage 2",
                "order": 2,
                "planned_start": datetime(2026, 2, 1, tzinfo=UTC),
            },
        )
        stages = await get_stages_by_project_id(test_session, test_project.id)
        assert len(stages) == EXPECTED_TWO_ITEMS
        assert stages[0].order == EXPECTED_ONE_ITEM
        assert stages[1].order == EXPECTED_TWO_ITEMS

    async def test_update_stage_status(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test updating stage status."""
        stage = await create_stage(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Design Phase",
                "order": 1,
                "planned_start": datetime(2026, 1, 1, tzinfo=UTC),
            },
        )
        updated = await update_stage_status(
            test_session,
            stage.id,
            "in_progress",
        )
        assert updated is not None
        assert updated.status == "in_progress"

    async def test_delete_stage(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test deleting stage."""
        stage = await create_stage(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Design Phase",
                "order": 1,
                "planned_start": datetime(2026, 1, 1, tzinfo=UTC),
            },
        )
        deleted = await delete_stage(test_session, stage.id)
        assert deleted is True
        retrieved = await get_stage_by_id(test_session, stage.id)
        assert retrieved is None


@pytest.mark.asyncio
class TestStatisticsCRUD:
    """Tests for statistics CRUD operations."""

    async def test_get_projects_count_by_status(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting projects count by status."""
        await create_project_for_stats(
            test_session,
            test_user.id,
            ProjectStatus.DRAFT,
        )
        await create_project_for_stats(
            test_session,
            test_user.id,
            ProjectStatus.IN_PROGRESS,
        )
        await create_project_for_stats(
            test_session,
            test_user.id,
            ProjectStatus.IN_PROGRESS,
        )
        stats = await get_projects_count_by_status(test_session)
        assert stats[ProjectStatus.DRAFT] == EXPECTED_ONE_ITEM
        assert stats[ProjectStatus.IN_PROGRESS] == EXPECTED_TWO_ITEMS

    async def test_get_tasks_count_by_status(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting tasks count by status."""
        await create_task_for_stats(
            test_session,
            test_project.id,
            TaskStatus.PENDING,
        )
        await create_task_for_stats(
            test_session,
            test_project.id,
            TaskStatus.IN_PROGRESS,
        )
        await create_task_for_stats(
            test_session,
            test_project.id,
            TaskStatus.IN_PROGRESS,
        )
        stats = await get_tasks_count_by_status(test_session)
        assert stats[TaskStatus.PENDING] == EXPECTED_ONE_ITEM
        assert stats[TaskStatus.IN_PROGRESS] == EXPECTED_TWO_ITEMS

    async def test_get_users_count_by_role(
        self,
        test_session: object,
    ) -> None:
        """Test getting users count by role."""
        await create_user_for_stats(test_session, UserRole.CLIENT)
        await create_user_for_stats(test_session, UserRole.MANAGER)
        await create_user_for_stats(test_session, UserRole.MANAGER)
        stats = await get_users_count_by_role(test_session)
        assert stats[UserRole.CLIENT] >= EXPECTED_ONE_ITEM
        assert stats[UserRole.MANAGER] >= EXPECTED_TWO_ITEMS

    async def test_get_total_projects_count(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting total projects count."""
        initial = await get_total_projects_count(test_session)
        await create_project_for_stats(
            test_session,
            test_user.id,
            ProjectStatus.DRAFT,
        )
        final = await get_total_projects_count(test_session)
        assert final == initial + 1

    async def test_get_total_tasks_count(
        self,
        test_session: object,
        test_project: object,
    ) -> None:
        """Test getting total tasks count."""
        initial = await get_total_tasks_count(test_session)
        await create_task_for_stats(
            test_session,
            test_project.id,
            TaskStatus.PENDING,
        )
        final = await get_total_tasks_count(test_session)
        assert final == initial + 1

    async def test_get_total_users_count(
        self,
        test_session: object,
    ) -> None:
        """Test getting total users count."""
        initial = await get_total_users_count(test_session)
        await create_user_for_stats(test_session, UserRole.CLIENT)
        final = await get_total_users_count(test_session)
        assert final == initial + 1

    async def test_get_manager_projects_count(
        self,
        test_session: object,
        test_user: object,
    ) -> None:
        """Test getting manager projects count."""
        await create_project(
            test_session,
            {
                "title": "Manager Project",
                "client_id": test_user.id,
                "manager_id": test_user.id,
                "status": ProjectStatus.DRAFT,
            },
        )
        count = await get_manager_projects_count(test_session, test_user.id)
        assert count >= 1

    async def test_get_performer_tasks_count(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting performer tasks count."""
        await create_task(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Performer Task",
                "performer_id": test_user.id,
                "status": TaskStatus.PENDING,
                "priority": 3,
            },
        )
        count = await get_performer_tasks_count(test_session, test_user.id)
        assert count >= 1


@pytest.mark.asyncio
class TestClientCompanyCRUD:
    """Tests for client company CRUD operations."""

    async def test_create_company(
        self,
        test_session: object,
    ) -> None:
        """Test creating company."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: TEST_COMPANY_NAME,
                "inn": "1234567890",
                "email": "test@company.com",
            },
        )
        assert company.name == TEST_COMPANY_NAME
        assert company.inn == "1234567890"

    async def test_get_company_by_id(
        self,
        test_session: object,
    ) -> None:
        """Test getting company by ID."""
        company = await create_company(
            test_session,
            {
                _NAME_KEY: TEST_COMPANY_NAME,
                "inn": "1234567890",
            },
        )
        retrieved = await get_company_by_id(test_session, company.id)
        assert retrieved is not None
        assert retrieved.name == TEST_COMPANY_NAME

    async def test_get_all_companies(
        self,
        test_session: object,
    ) -> None:
        """Test getting all companies."""
        await create_company(
            test_session,
            {"name": "Company 1"},
        )
        await create_company(
            test_session,
            {"name": "Company 2"},
        )
        companies = await get_all_companies(test_session)
        assert len(companies) >= EXPECTED_TWO_ITEMS

    async def test_update_company(
        self,
        test_session: object,
    ) -> None:
        """Test updating company."""
        company = await create_company(
            test_session,
            {"name": "Test Company"},
        )
        updated = await update_company(
            test_session,
            company.id,
            {"name": "Updated Company", "phone": "+79991234567"},
        )
        assert updated is not None
        assert updated.name == "Updated Company"

    async def test_delete_company(
        self,
        test_session: object,
    ) -> None:
        """Test deleting company."""
        company = await create_company(
            test_session,
            {"name": "Test Company"},
        )
        deleted = await delete_company(test_session, company.id)
        assert deleted is True
        retrieved = await get_company_by_id(test_session, company.id)
        assert retrieved is None


@pytest.mark.asyncio
class TestGISLogCRUD:
    """Tests for GIS log CRUD operations."""

    async def test_create_gis_check_log(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test creating GIS check log."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_HOUR, TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        log = await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: "Test Address",
                _COORDINATES_KEY: "30.3158,59.9391",
                _INSIDE_ZONE_KEY: True,
            },
        )
        assert log.address == "Test Address"
        assert log.inside_zone is True

    async def test_get_gis_logs_by_meeting_id(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test getting GIS logs by meeting ID."""
        meeting = await create_meeting(
            test_session,
            {
                _PROJECT_ID_KEY: test_project.id,
                _TITLE_KEY: TEST_MEETING_TITLE,
                _ORGANIZER_ID_KEY: test_user.id,
                _SCHEDULED_AT_KEY: datetime(
                    TEST_YEAR, TEST_MONTH, TEST_DAY,
                    TEST_HOUR, TEST_MINUTE, tzinfo=UTC,
                ),
            },
        )
        await create_gis_check_log(
            test_session,
            {
                _MEETING_ID_KEY: meeting.id,
                _ADDRESS_KEY: "Address 1",
                "coordinates": "30.3158,59.9391",
                "inside_zone": True,
            },
        )
        await create_gis_check_log(
            test_session,
            {
                "meeting_id": meeting.id,
                "address": "Address 2",
                "coordinates": "30.3159,59.9392",
                "inside_zone": False,
            },
        )
        logs = await get_gis_logs_by_meeting_id(test_session, meeting.id)
        assert len(logs) == EXPECTED_TWO_ITEMS

    async def test_delete_gis_log(
        self,
        test_session: object,
        test_project: object,
        test_user: object,
    ) -> None:
        """Test deleting GIS log."""
        meeting = await create_meeting(
            test_session,
            {
                "project_id": test_project.id,
                "title": "Test Meeting",
                "organizer_id": test_user.id,
                "scheduled_at": datetime(2026, 12, 31, 10, 0, tzinfo=UTC),
            },
        )
        log = await create_gis_check_log(
            test_session,
            {
                "meeting_id": meeting.id,
                "address": "Test Address",
                "coordinates": "30.3158,59.9391",
                "inside_zone": True,
            },
        )
        deleted = await delete_gis_log(test_session, log.id)
        assert deleted is True
        logs = await get_gis_logs_by_meeting_id(test_session, meeting.id)
        assert len(logs) == 0


async def create_project_for_stats(
    session: object,
    client_id: int,
    status: ProjectStatus,
) -> Project:
    """Create project for statistics tests."""
    return await create_project(
        session,
        {
            "title": f"Stats Project {status.value}",
            "client_id": client_id,
            "status": status,
        },
    )


async def create_task_for_stats(
    session: object,
    project_id: int,
    status: TaskStatus,
) -> Task:
    """Create task for statistics tests."""
    return await create_task(
        session,
        {
            "project_id": project_id,
            "title": f"Stats Task {status.value}",
            "status": status,
            "priority": 3,
        },
    )


async def create_user_for_stats(
    session: object,
    role: UserRole,
) -> User:
    """Create user for statistics tests."""
    return await create_user(
        session,
        {
            "telegram_id": TEST_TELEGRAM_ID_MIN + secrets.randbelow(
                TEST_TELEGRAM_ID_MAX - TEST_TELEGRAM_ID_MIN,
            ),
            "username": f"statsuser_{role.value}",
            "first_name": "Stats",
            "last_name": "User",
            "role": role,
        },
    )
