"""Enum types for the application."""

from enum import StrEnum

# Common string values for enums
_PENDING = "pending"
_IN_PROGRESS = "in_progress"
_COMPLETED = "completed"
_CANCELLED = "cancelled"
_CONFIRMED = "confirmed"


class UserRole(StrEnum):
    """User roles in the system."""

    CLIENT = "client"
    MANAGER = "manager"
    PERFORMER = "performer"


class ProjectStatus(StrEnum):
    """Project status values."""

    DRAFT = "draft"
    PENDING = _PENDING
    REGISTERED = "registered"
    IN_PROGRESS = _IN_PROGRESS
    ON_HOLD = "on_hold"
    COMPLETED = _COMPLETED
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    """Task status values."""

    PENDING = _PENDING
    IN_PROGRESS = _IN_PROGRESS
    REVIEW = "review"
    COMPLETED = _COMPLETED
    CANCELLED = _CANCELLED


class DocumentType(StrEnum):
    """Document type values."""

    SOURCE = "source"
    WORK = "work"
    DOCUMENT_RESULT = "result"
    OTHER = "other"


class MeetingStatus(StrEnum):
    """Meeting status values."""

    PENDING = _PENDING
    CONFIRMED = _CONFIRMED
    CANCELLED = _CANCELLED
    COMPLETED = _COMPLETED


class MeetingParticipantStatus(StrEnum):
    """Meeting participant status values."""

    PENDING = _PENDING
    CONFIRMED = _CONFIRMED
    DECLINED = "declined"


class NotificationType(StrEnum):
    """Notification type values."""

    NEW_PROJECT = "new_project"
    PROJECT_REGISTERED = "project_registered"
    NEW_TASK = "new_task"
    DEADLINE_SOON = "deadline_soon"
    MEETING_INVITE = "meeting_invite"
    MEETING_REMINDER = "meeting_reminder"
    PROJECT_STATUS_CHANGED = "project_status_changed"
    DOCUMENT_UPLOADED = "document_uploaded"
    STAGE_COMPLETED = "stage_completed"
    TASK_COMPLETED = "task_completed"
