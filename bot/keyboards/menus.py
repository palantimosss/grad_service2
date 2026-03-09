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


def get_role_keyboard() -> InlineKeyboardMarkup:
    """Get role selection keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Клиент", callback_data="role_client")
    builder.button(text="Руководитель", callback_data="role_manager")
    builder.button(text="Исполнитель", callback_data="role_performer")
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_keyboard(role: UserRole) -> InlineKeyboardMarkup:
    """Get main menu keyboard based on role."""
    builder = InlineKeyboardBuilder()

    if role == UserRole.CLIENT:
        builder.button(text="Мои проекты", callback_data="my_projects")
        builder.button(text="Создать проект", callback_data="create_project")
        builder.button(text="Профиль", callback_data="profile")
    elif role == UserRole.MANAGER:
        builder.button(text="Все проекты", callback_data="all_projects")
        builder.button(text="Заявки", callback_data="pending_projects")
        builder.button(text="Задачи", callback_data="all_tasks")
        builder.button(text="Клиенты", callback_data="clients")
        builder.button(text="Статистика", callback_data="statistics")
        builder.button(text="Профиль", callback_data="profile")
    elif role == UserRole.PERFORMER:
        builder.button(text="Мои задачи", callback_data="my_tasks")
        builder.button(text="Проекты", callback_data="projects")
        builder.button(text="Профиль", callback_data="profile")

    builder.adjust(1)
    return builder.as_markup()


def get_profile_keyboard() -> InlineKeyboardMarkup:
    """Get profile keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Редактировать", callback_data="edit_profile")
    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(2)
    return builder.as_markup()


def get_edit_profile_keyboard() -> InlineKeyboardMarkup:
    """Get edit profile keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Телефон", callback_data="edit_phone")
    builder.button(text="Email", callback_data="edit_email")
    builder.button(text="Должность", callback_data="edit_position")
    builder.button(text="Назад", callback_data="back_to_profile")
    builder.adjust(2)
    return builder.as_markup()


def get_projects_keyboard(projects: list) -> InlineKeyboardMarkup:
    """Get projects list keyboard."""
    builder = InlineKeyboardBuilder()
    for project in projects:
        builder.button(
            text=f"📁 {project.title}",
            callback_data=f"project_{project.id}",
        )
    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_project_actions_keyboard(
    project_id: int, role: UserRole,
) -> InlineKeyboardMarkup:
    """Get project actions keyboard."""
    builder = InlineKeyboardBuilder()

    if role == UserRole.CLIENT:
        builder.button(
            text="Загрузить документ",
            callback_data=f"upload_doc_{project_id}",
        )
        builder.button(
            text="Обратная связь",
            callback_data=f"feedback_{project_id}",
        )
    elif role == UserRole.MANAGER:
        builder.button(
            text="Создать задачу",
            callback_data=f"create_task_{project_id}",
        )
        builder.button(
            text="Создать этап",
            callback_data=f"create_stage_{project_id}",
        )
        builder.button(
            text="Создать встречу",
            callback_data=f"create_meeting_{project_id}",
        )
        builder.button(
            text="Статус проекта",
            callback_data=f"project_status_{project_id}",
        )
    elif role == UserRole.PERFORMER:
        builder.button(
            text="Загрузить документ",
            callback_data=f"upload_doc_{project_id}",
        )

    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_project_status_keyboard(project_id: int) -> InlineKeyboardMarkup:
    """Get project status change keyboard."""
    builder = InlineKeyboardBuilder()
    for status in ProjectStatus:
        builder.button(
            text=status.value.replace("_", " ").title(),
            callback_data=f"set_status_{project_id}_{status.value}",
        )
    builder.button(text="Назад", callback_data="back_to_project")
    builder.adjust(2)
    return builder.as_markup()


def get_tasks_keyboard(tasks: list) -> InlineKeyboardMarkup:
    """Get tasks list keyboard."""
    builder = InlineKeyboardBuilder()
    for task in tasks:
        emoji = "⏳" if task.status == TaskStatus.PENDING else "✅"
        builder.button(
            text=f"{emoji} {task.title}",
            callback_data=f"task_{task.id}",
        )
    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_task_actions_keyboard(
    task_id: int, status: TaskStatus,
) -> InlineKeyboardMarkup:
    """Get task actions keyboard."""
    builder = InlineKeyboardBuilder()

    if status == TaskStatus.PENDING:
        builder.button(
            text="Взять в работу",
            callback_data=f"task_start_{task_id}",
        )
    elif status == TaskStatus.IN_PROGRESS:
        builder.button(
            text="Завершить",
            callback_data=f"task_complete_{task_id}",
        )

    builder.button(
        text="Загрузить документ",
        callback_data=f"upload_doc_task_{task_id}",
    )
    builder.button(text="Назад", callback_data="back_to_tasks")
    builder.adjust(1)
    return builder.as_markup()


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
    builder.button(text="Назад", callback_data=back_callback)
    builder.adjust(1)
    return builder.as_markup()


def get_document_download_keyboard(
    document_id: int,
    can_delete: bool = False,  # noqa: FBT001, FBT002
) -> InlineKeyboardMarkup:
    """Get document download keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Скачать",
        callback_data=f"download_doc_{document_id}",
    )
    if can_delete:
        builder.button(
            text="Удалить",
            callback_data=f"delete_doc_{document_id}",
        )
    builder.button(text="Назад", callback_data="back_to_documents")
    builder.adjust(2)
    return builder.as_markup()


def get_document_type_keyboard() -> InlineKeyboardMarkup:
    """Get document type selection keyboard."""
    builder = InlineKeyboardBuilder()
    for doc_type in DocumentType:
        builder.button(
            text=doc_type.value.replace("_", " ").title(),
            callback_data=f"doc_type_{doc_type.value}",
        )
    builder.adjust(2)
    return builder.as_markup()


def get_meetings_keyboard(meetings: list) -> InlineKeyboardMarkup:
    """Get meetings list keyboard."""
    builder = InlineKeyboardBuilder()
    for meeting in meetings:
        status_emoji = {
            MeetingStatus.PENDING: "⏳",
            MeetingStatus.CONFIRMED: "✅",
            MeetingStatus.CANCELLED: "❌",
            MeetingStatus.COMPLETED: "✔️",
        }
        emoji = status_emoji.get(meeting.status, "📅")
        builder.button(
            text=f"{emoji} {meeting.title}",
            callback_data=f"meeting_{meeting.id}",
        )
    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_meeting_response_keyboard(
    meeting_id: int,
) -> InlineKeyboardMarkup:
    """Get meeting response keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Подтвердить",
        callback_data=f"meeting_confirm_{meeting_id}",
    )
    builder.button(
        text="Отклонить",
        callback_data=f"meeting_decline_{meeting_id}",
    )
    builder.button(text="Назад", callback_data="back_to_meetings")
    builder.adjust(2)
    return builder.as_markup()


def get_yes_no_keyboard() -> InlineKeyboardMarkup:
    """Get yes/no keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="yes")
    builder.button(text="Нет", callback_data="no")
    builder.adjust(2)
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Get cancel keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Отмена", callback_data="cancel")
    return builder.as_markup()


def get_clients_keyboard(companies: list) -> InlineKeyboardMarkup:
    """Get clients list keyboard."""
    builder = InlineKeyboardBuilder()
    for company in companies:
        builder.button(
            text=f"🏢 {company.name}",
            callback_data=f"client_{company.id}",
        )
    builder.button(text="Добавить клиента", callback_data="add_client")
    builder.button(text="Назад", callback_data="back_to_menu")
    builder.adjust(1)
    return builder.as_markup()


def get_notification_keyboard(
    notification_id: int,
) -> InlineKeyboardMarkup:
    """Get notification keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отметить прочитанным",
        callback_data=f"notif_read_{notification_id}",
    )
    builder.button(text="Назад", callback_data="back_to_notifications")
    builder.adjust(1)
    return builder.as_markup()


def get_back_keyboard(callback: str = "back_to_menu") -> InlineKeyboardMarkup:
    """Get simple back keyboard."""
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=callback)
    return builder.as_markup()
