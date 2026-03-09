"""CRUD parameter classes."""

from bot.database.crud_modules.client_company_crud import (
    CompanyCreateParams,
)
from bot.database.crud_modules.document_crud import DocumentCreateParams
from bot.database.crud_modules.feedback_crud import FeedbackCreateParams
from bot.database.crud_modules.gis_log_crud import GISLogCreateParams
from bot.database.crud_modules.meeting_crud import MeetingCreateParams
from bot.database.crud_modules.notification_crud import (
    NotificationCreateParams,
)
from bot.database.crud_modules.project_crud import ProjectCreateParams
from bot.database.crud_modules.stage_crud import StageCreateParams
from bot.database.crud_modules.task_crud import TaskCreateParams
from bot.database.crud_modules.user_crud import (
    UserCreateParams,
    UserUpdateParams,
)

__all__ = [
    "CompanyCreateParams",
    "DocumentCreateParams",
    "FeedbackCreateParams",
    "GISLogCreateParams",
    "MeetingCreateParams",
    "NotificationCreateParams",
    "ProjectCreateParams",
    "StageCreateParams",
    "TaskCreateParams",
    "UserCreateParams",
    "UserUpdateParams",
]
