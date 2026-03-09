"""FSM states for the bot."""

from aiogram.fsm.state import State, StatesGroup


class UserRegistration(StatesGroup):
    """User registration states."""

    role = State()
    phone = State()
    email = State()
    position = State()
    consent = State()


class ProfileEdit(StatesGroup):
    """Profile editing states."""

    field = State()
    value = State()


class ProjectCreation(StatesGroup):
    """Project creation states."""

    title = State()
    description = State()
    deadline = State()
    budget = State()


class TaskCreation(StatesGroup):
    """Task creation states."""

    title = State()
    description = State()
    performer = State()
    deadline = State()
    priority = State()


class StageCreation(StatesGroup):
    """Stage creation states."""

    title = State()
    description = State()
    planned_start = State()
    planned_end = State()
    order = State()


class MeetingCreation(StatesGroup):
    """Meeting creation states."""

    title = State()
    description = State()
    scheduled_at = State()
    duration = State()
    format_type = State()
    address = State()
    online_link = State()


class DocumentUpload(StatesGroup):
    """Document upload states."""

    project = State()
    task = State()
    document_type = State()
    description = State()
    file = State()


class FeedbackCreation(StatesGroup):
    """Feedback creation states."""

    project = State()
    message = State()
    rating = State()


class CompanyCreation(StatesGroup):
    """Company creation states."""

    name = State()
    inn = State()
    kpp = State()
    address = State()
    phone = State()
    email = State()
    website = State()
