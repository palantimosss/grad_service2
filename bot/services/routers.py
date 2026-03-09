"""Routers registration module."""


from typing import TYPE_CHECKING

from bot.handlers.client import client_router
from bot.handlers.common import common_router
from bot.handlers.manager import manager_router
from bot.handlers.notifications import notifications_router
from bot.handlers.performer import performer_router

if TYPE_CHECKING:
    from aiogram import Dispatcher


def register_routers(dispatcher: Dispatcher) -> None:
    """Register all routers with dispatcher."""
    dispatcher.include_routers(
        common_router,
        client_router,
        manager_router,
        performer_router,
        notifications_router,
    )
