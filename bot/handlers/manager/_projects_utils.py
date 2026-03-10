"""Project handlers for manager - user utils."""

from bot.database.crud_modules.user_crud import get_user_by_telegram_id

__all__ = (  # noqa: WPS410
    "get_user_by_telegram_id",
)
