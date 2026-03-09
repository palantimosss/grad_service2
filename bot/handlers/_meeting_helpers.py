"""Meeting creation helper functions."""

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from bot.database.crud_modules.meeting_crud import create_meeting
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session

if TYPE_CHECKING:
    from aiogram import types
    from aiogram.fsm.context import FSMContext

# Skip option text
_SKIP_OPTION = "пропустить"

# Default values
_DEFAULT_DURATION = 60

# Optional meeting fields
_OPTIONAL_MEETING_FIELDS = (
    "description",
    "address",
    "coordinates",
    "online_link",
    "gis_check_result",
)


def parse_datetime(text: str) -> datetime | None:
    """Parse datetime from text."""
    try:
        return datetime.strptime(text, "%d.%m.%Y %H:%M").replace(
            tzinfo=UTC,
        )
    except ValueError:
        return None


def add_optional_param(
    meeting_params: dict, meeting_data: dict, field_key: str,
) -> None:
    """Add optional parameter to params if present in data."""
    if meeting_data.get(field_key):
        meeting_params[field_key] = meeting_data[field_key]


def build_meeting_params(
    meeting_data: dict, user_id: int,
) -> dict:
    """Build meeting creation params."""
    meeting_params: dict = {
        "project_id": meeting_data["project_id"],
        "title": meeting_data["title"],
        "organizer_id": user_id,
        "scheduled_at": meeting_data["scheduled_at"],
        "duration_minutes": meeting_data.get("duration", _DEFAULT_DURATION),
        "is_online": meeting_data.get("is_online", False),
    }
    for field_key in _OPTIONAL_MEETING_FIELDS:
        add_optional_param(meeting_params, meeting_data, field_key)
    return meeting_params


def format_coordinates(coordinates: tuple) -> str:
    """Format coordinates as string."""
    return f"{coordinates[0]},{coordinates[1]}"


def get_gis_status(*, is_inside: bool) -> str:
    """Get GIS status string."""
    return "inside" if is_inside else "outside"


def get_skip_option() -> str:
    """Get skip option text."""
    return _SKIP_OPTION


def get_default_duration() -> int:
    """Get default meeting duration."""
    return _DEFAULT_DURATION


async def create_meeting_in_db(
    message: types.Message,
    meeting_data: dict,
) -> None:
    """Create meeting in database."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        meeting_params = build_meeting_params(meeting_data, user.id)
        await create_meeting(session=session, params=meeting_params)


async def handle_gis_result(
    message: types.Message,
    state: FSMContext,
    address_val: str,
    gis_result: object,
) -> bool:
    """Handle GIS check result. Returns True if should continue."""
    await state.update_data(
        address=address_val,
        coordinates=format_coordinates(gis_result.coordinates),
        gis_check_result=get_gis_status(is_inside=gis_result.inside_zone),
    )
    if not gis_result.inside_zone:
        await message.answer(
            f"⚠️ {gis_result.message}\n"
            "Рекомендуем онлайн-встречу. Продолжить? (да/нет):",
        )
        return False
    return True
