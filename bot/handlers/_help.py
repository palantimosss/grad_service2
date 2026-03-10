"""Help and menu handlers."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types
from aiogram.filters import Command

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.keyboards.menus import get_main_menu_keyboard

logger = logging.getLogger(__name__)

help_router = Router()

HELP_TEXT = (
    "<b>Grad Service - Управление проектами</b>\n\n"
    "Команды:\n"
    "/start - Регистрация\n"
    "/menu - Главное меню\n"
    "/help - Эта справка\n"
    "/profile - Мой профиль\n\n"
    "Для помощи обратитесь к руководителю проекта."
)


@help_router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Handle /help command."""
    await message.answer(HELP_TEXT)


@help_router.callback_query(
    lambda callback: callback.data == "back_to_menu",
)
async def back_to_menu(callback: types.CallbackQuery) -> None:
    """Return to main menu."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if user:
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=get_main_menu_keyboard(user.role),
            )


@help_router.callback_query(
    lambda callback: callback.data == "cancel",
)
async def cancel_action(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Cancel current action."""
    await state.clear()
    await callback.message.edit_text("Действие отменено.")
    await cmd_menu(callback.message)


@help_router.message(Command("menu"))
async def cmd_menu(message: types.Message) -> None:
    """Handle /menu command."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user:
            await message.answer(
                "Главное меню:",
                reply_markup=get_main_menu_keyboard(user.role),
            )
        else:
            await message.answer(
                "Сначала зарегистрируйтесь командой /start",
            )
