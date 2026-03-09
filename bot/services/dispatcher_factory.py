"""Dispatcher factory module."""

from aiogram import Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.middleware.logging import LoggingMiddleware


def create_dispatcher() -> Dispatcher:
    """Create and configure dispatcher."""
    storage = MemoryStorage()
    dispatcher = Dispatcher(storage=storage)

    dispatcher.update.middleware(LoggingMiddleware())

    return dispatcher
