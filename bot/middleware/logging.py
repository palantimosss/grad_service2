"""Logging middleware module."""

import logging
from typing import TYPE_CHECKING, Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseMiddleware):
    """Middleware for logging updates."""

    async def __call__(
        self,
        request_handler: Callable[[Any, dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        handler_data: dict[str, Any],
    ) -> object:
        """Log incoming update."""
        if isinstance(event, Message):
            logger.info(
                "Message from %s: %s",
                event.from_user.username or event.from_user.id,
                event.text,
            )
        elif isinstance(event, CallbackQuery):
            logger.info(
                "Callback from %s: %s",
                event.from_user.username or event.from_user.id,
                event.data,
            )
        return await request_handler(event, handler_data)
