"""Main entry point for Grad Service Telegram Bot."""

import asyncio
import logging

from bot.services.bot_factory import create_bot
from bot.services.dispatcher_factory import create_dispatcher
from bot.services.routers import register_routers
from bot.services.scheduler import create_scheduler
from bot.services.startup import on_shutdown, on_startup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


async def main() -> None:
    """Run the bot."""
    bot = create_bot()
    dispatcher = create_dispatcher()

    register_routers(dispatcher)

    create_scheduler()

    dispatcher.startup.register(on_startup)
    dispatcher.shutdown.register(on_shutdown)

    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
