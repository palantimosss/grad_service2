"""Keyboards package."""

from bot.keyboards._clients import get_clients_keyboard
from bot.keyboards._common import (
    _BACK_DOCUMENTS,
    _BACK_MEETINGS,
    _BACK_MENU,
    _BACK_NOTIFICATIONS,
    _BACK_PROJECT,
    _BACK_TASKS,
    get_back_keyboard,
    get_cancel_keyboard,
    get_yes_no_keyboard,
)
from bot.keyboards._documents import (
    get_document_download_keyboard,
    get_document_type_keyboard,
    get_documents_keyboard,
)
from bot.keyboards._meetings import (
    get_meeting_response_keyboard,
    get_meetings_keyboard,
)
from bot.keyboards._profile import (
    get_edit_profile_keyboard,
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_role_keyboard,
)
from bot.keyboards._projects import (
    get_project_actions_keyboard,
    get_project_status_keyboard,
    get_projects_keyboard,
)
from bot.keyboards._tasks import (
    get_task_actions_keyboard,
    get_tasks_keyboard,
)

__all__ = (
    "_BACK_DOCUMENTS",
    "_BACK_MEETINGS",
    "_BACK_MENU",
    "_BACK_NOTIFICATIONS",
    "_BACK_PROJECT",
    "_BACK_TASKS",
    "get_back_keyboard",
    "get_cancel_keyboard",
    "get_clients_keyboard",
    "get_document_download_keyboard",
    "get_document_type_keyboard",
    "get_documents_keyboard",
    "get_edit_profile_keyboard",
    "get_main_menu_keyboard",
    "get_meeting_response_keyboard",
    "get_meetings_keyboard",
    "get_profile_keyboard",
    "get_project_actions_keyboard",
    "get_project_status_keyboard",
    "get_projects_keyboard",
    "get_role_keyboard",
    "get_task_actions_keyboard",
    "get_tasks_keyboard",
    "get_yes_no_keyboard",
)
