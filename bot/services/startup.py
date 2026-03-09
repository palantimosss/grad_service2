"""Startup and shutdown hooks."""

import logging
from typing import TYPE_CHECKING

from bot.database.database import create_tables

if TYPE_CHECKING:
    from aiogram import Bot

logger = logging.getLogger(__name__)


async def on_startup(
    bot: Bot,
) -> None:
    """Execute on bot startup."""
    logger.info("Bot starting up...")
    await create_tables()
    logger.info("Database tables created")

    bot_info = await bot.get_me()
    logger.info("Bot connected: @%s", bot_info.username)


async def on_shutdown(
    bot: Bot,
) -> None:
    """Execute on bot shutdown."""
    logger.info("Bot shutting down...")
    await bot.session.close()
    logger.info("Bot session closed")
