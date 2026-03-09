"""Enum types for the application."""

from enum import StrEnum


class UserRole(StrEnum):
    """User roles in the system."""

    CLIENT = "client"
    MANAGER = "manager"
    PERFORMER = "performer"


class ProjectStatus(StrEnum):
    """Project status values."""

    DRAFT = "draft"
    PENDING = "pending"
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TaskStatus(StrEnum):
    """Task status values."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DocumentType(StrEnum):
    """Document type values."""

    SOURCE = "source"
    WORK = "work"
    RESULT = "result"
    OTHER = "other"


class MeetingStatus(StrEnum):
    """Meeting status values."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class MeetingParticipantStatus(StrEnum):
    """Meeting participant status values."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
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
