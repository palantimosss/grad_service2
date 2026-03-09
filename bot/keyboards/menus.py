"""Inline keyboards for the bot."""

from typing import TYPE_CHECKING

from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.models.enums import (
    DocumentType,
    MeetingStatus,
    ProjectStatus,
    TaskStatus,
    UserRole,
)

if TYPE_CHECKING:
    from aiogram.types import InlineKeyboardMarkup

# Button text constants
_BACK_TEXT = "Назад"
_CANCEL_TEXT = "Отмена"
_YES_TEXT = "Да"
_NO_TEXT = "Нет"

# Callback data constants
_BACK_MENU = "back_to_menu"
_BACK_PROFILE = "back_to_profile"
_BACK_PROJECT = "back_to_project"
_BACK_TASKS = "back_to_tasks"
_BACK_MEETINGS = "back_to_meetings"
_BACK_DOCUMENTS = "back_to_documents"
_BACK_NOTIFICATIONS = "back_to_notifications"


def _adjust_single(builder: InlineKeyboardBuilder) -> None:
    """Adjust builder to single column."""
    builder.adjust(1)


def _adjust_double(builder: InlineKeyboardBuilder) -> None:
    """Adjust builder to double column."""
    builder.adjust(2)


def _build_single_column_keyboard(
    buttons: list[tuple[str, str]],
) -> InlineKeyboardMarkup:
    """Build single column keyboard from button list."""
    builder = InlineKeyboardBuilder()
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    _adjust_single(builder)
    return builder.as_markup()


def _build_double_column_keyboard(
    buttons: list[tuple[str, str]],
) -> InlineKeyboardMarkup:
    """Build double column keyboard from button list."""
    builder = InlineKeyboardBuilder()
    for text, callback in buttons:
        builder.button(text=text, callback_data=callback)
    _adjust_double(builder)
    return builder.as_markup()


def get_role_keyboard() -> InlineKeyboardMarkup:
    """Get role selection keyboard."""
    return _build_single_column_keyboard([
        ("Клиент", "role_client"),
        ("Руководитель", "role_manager"),
        ("Исполнитель", "role_performer"),
    ])


def get_main_menu_keyboard(role: UserRole) -> InlineKeyboardMarkup:
    """Get main menu keyboard based on role."""
    if role == UserRole.CLIENT:
        return _build_single_column_keyboard([
            ("Мои проекты", "my_projects"),
            ("Создать проект", "create_project"),
            ("Профиль", "profile"),
        ])
    elif role == UserRole.MANAGER:
        return _build_single_column_keyboard([
            ("Все проекты", "all_projects"),
            ("Заявки", "pending_projects"),
            ("Задачи", "all_tasks"),
            ("Клиенты", "clients"),
            ("Статистика", "statistics"),
            ("Профиль", "profile"),
        ])
    else:  # PERFORMER
        return _build_single_column_keyboard([
            ("Мои задачи", "my_tasks"),
            ("Проекты", "projects"),
            ("Профиль", "profile"),
        ])


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Get profile keyboard."""
    return _build_double_column_keyboard([
        ("Редактировать", "edit_profile"),
        (_BACK_TEXT, _BACK_MENU),
    ])


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Get edit profile keyboard."""
    return _build_double_column_keyboard([
        ("Телефон", "edit_phone"),
        ("Email", "edit_email"),
        ("Должность", "edit_position"),
        (_BACK_TEXT, _BACK_PROFILE),
    ])


def get_projects_keyboard(projects: list) -> InlineKeyboardMarkup:
    """Get projects list keyboard."""
    builder = InlineKeyboardBuilder()
    for project in projects:
        builder.button(
            text=f"📁 {project.title}",
            callback_data=f"project_{project.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def _get_project_action_buttons(
    project_id: int, role: UserRole,
) -> list[tuple[str, str]]:
    """Get project action buttons based on role."""
    if role == UserRole.CLIENT:
        return [
            ("Загрузить документ", f"upload_doc_{project_id}"),
            ("Обратная связь", f"feedback_{project_id}"),
            (_BACK_TEXT, _BACK_MENU),
        ]
    elif role == UserRole.MANAGER:
        return [
            ("Создать задачу", f"create_task_{project_id}"),
            ("Создать этап", f"create_stage_{project_id}"),
            ("Создать встречу", f"create_meeting_{project_id}"),
            ("Статус проекта", f"project_status_{project_id}"),
            (_BACK_TEXT, _BACK_MENU),
        ]
    else:  # PERFORMER
        return [
            ("Загрузить документ", f"upload_doc_{project_id}"),
            (_BACK_TEXT, _BACK_MENU),
        ]


def get_project_actions_keyboard(
    project_id: int, role: UserRole,
) -> InlineKeyboardMarkup:
    """Get project actions keyboard."""
    buttons = _get_project_action_buttons(project_id, role)
    return _build_single_column_keyboard(buttons)


def get_project_status_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Get project status change keyboard."""
    builder = InlineKeyboardBuilder()
    for status in ProjectStatus:
        builder.button(
            text=status.value.replace("_", " ").title(),
            callback_data=f"set_status_{project_id}_{status.value}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_PROJECT)
    _adjust_double(builder)
    return builder.as_markup()


def _get_task_emoji(status: TaskStatus) -> str:
    """Get emoji for task status."""
    return "⏳" if status == TaskStatus.PENDING else "✅"


def get_tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Get tasks list keyboard."""
    builder = InlineKeyboardBuilder()
    for task in tasks:
        emoji = _get_task_emoji(task.status)
        builder.button(
            text=f"{emoji} {task.title}",
            callback_data=f"task_{task.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def _get_task_action_buttons(
    task_id: int, status: TaskStatus,
) -> list[tuple[str, str]]:
    """Get task action buttons based on status."""
    buttons = []
    if status == TaskStatus.PENDING:
        buttons.append(("Взять в работу", f"task_start_{task_id}"))
    elif status == TaskStatus.IN_PROGRESS:
        buttons.append(("Завершить", f"task_complete_{task_id}"))
    buttons.append(("Загрузить документ", f"upload_doc_task_{task_id}"))
    buttons.append((_BACK_TEXT, _BACK_TASKS))
    return buttons


def get_task_actions_keyboard(
    task_id: int, status: TaskStatus,
) -> InlineKeyboardMarkup:
    """Get task actions keyboard."""
    buttons = _get_task_action_buttons(task_id, status)
    return _build_single_column_keyboard(buttons)


def get_documents_keyboard(
    documents: list, project_id: int, task_id: int | None = None,
) -> InlineKeyboardMarkup:
    """Get documents list keyboard."""
    builder = InlineKeyboardBuilder()
    for doc in documents:
        builder.button(
            text=f"📄 {doc.file_name}",
            callback_data=f"doc_{doc.id}",
        )
    back_callback = f"task_{task_id}" if task_id else f"project_{project_id}"
    builder.button(text=_BACK_TEXT, callback_data=back_callback)
    _adjust_single(builder)
    return builder.as_markup()


def get_document_download_keyboard(
    document_id: int,
    can_delete: bool = False,  # noqa: FBT001, FBT002
) -> InlineKeyboardMarkup:
    """Get document download keyboard."""
    buttons = [("Скачать", f"download_doc_{document_id}")]
    if can_delete:
        buttons.append(("Удалить", f"delete_doc_{document_id}"))
    buttons.append((_BACK_TEXT, _BACK_DOCUMENTS))
    return _build_double_column_keyboard(buttons)


def get_document_type_keyboard() -> InlineKeyboardMarkup:
    """Get document type selection keyboard."""
    builder = InlineKeyboardBuilder()
    for doc_type in DocumentType:
        builder.button(
            text=doc_type.value.replace("_", " ").title(),
            callback_data=f"doc_type_{doc_type.value}",
        )
    _adjust_double(builder)
    return builder.as_markup()


def get_meetings_keyboard(meetings: list) -> InlineKeyboardMarkup:
    """Get meetings list keyboard."""
    builder = InlineKeyboardBuilder()
    for meeting in meetings:
        emoji = _get_meeting_emoji(meeting.status)
        builder.button(
            text=f"{emoji} {meeting.title}",
            callback_data=f"meeting_{meeting.id}",
        )
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def _get_meeting_emoji(status: MeetingStatus) -> str:
    """Get emoji for meeting status."""
    status_emoji = {
        MeetingStatus.PENDING: "⏳",
        MeetingStatus.CONFIRMED: "✅",
        MeetingStatus.CANCELLED: "❌",
        MeetingStatus.COMPLETED: "✔️",
    }
    return status_emoji.get(status, "📅")


def get_meeting_response_keyboard(
    meeting_id: int,
) -> InlineKeyboardMarkup:
    """Get meeting response keyboard."""
    return _build_double_column_keyboard([
        ("Подтвердить", f"meeting_confirm_{meeting_id}"),
        ("Отклонить", f"meeting_decline_{meeting_id}"),
        (_BACK_TEXT, _BACK_MEETINGS),
    ])


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Get yes/no keyboard."""
    return _build_double_column_keyboard([
        (_YES_TEXT, "yes"),
        (_NO_TEXT, "no"),
    ])


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    return _build_single_column_keyboard([
        (_CANCEL_TEXT, "cancel"),
    ])


def get_clients_keyboard(companies: list) -> InlineKeyboardMarkup:
    """Get clients list keyboard."""
    builder = InlineKeyboardBuilder()
    for company in companies:
        builder.button(
            text=f"🏢 {company.name}",
            callback_data=f"client_{company.id}",
        )
    builder.button(text="Добавить клиента", callback_data="add_client")
    builder.button(text=_BACK_TEXT, callback_data=_BACK_MENU)
    _adjust_single(builder)
    return builder.as_markup()


def get_notification_keyboard(
    notification_id: int,
) -> InlineKeyboardMarkup:
    """Get notification keyboard."""
    return _build_single_column_keyboard([
        ("Отметить прочитанным", f"notif_read_{notification_id}"),
        (_BACK_TEXT, _BACK_NOTIFICATIONS),
    ])


def get_back_keyboard(
    callback: str = _BACK_MENU,
) -> InlineKeyboardMarkup:
    """Get simple back keyboard."""
    return _build_single_column_keyboard([
        (_BACK_TEXT, callback),
    ])
