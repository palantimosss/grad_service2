"""Profile handlers."""

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types
from aiogram.filters import Command

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.user_crud import (
    UserUpdateParams,
    get_user_by_telegram_id,
    update_user_profile,
)
from bot.database.database import get_session
from bot.keyboards.menus import (
    get_back_keyboard,
    get_edit_profile_keyboard,
    get_profile_keyboard,
)
from bot.states.states import ProfileEdit

logger = logging.getLogger(__name__)

profile_router = Router()

_FIELD_NAMES = (
    ("phone", "телефон"),
    ("email", "email"),
    ("position", "должность"),
)


def _get_field_label(field_key: str) -> str:
    """Get field label from field key."""
    for key, label in _FIELD_NAMES:
        if key == field_key:
            return label
    return field_key


def _get_user_profile_values(user: object) -> dict[str, str]:
    """Get user profile values as dict."""
    return {
        "last_name": user.last_name or "",  # type: ignore[union-attr]
        "phone": user.phone or "Не указан",  # type: ignore[union-attr]
        "email": user.email or "Не указан",  # type: ignore[union-attr]
        "position": user.position or "Не указана",  # type: ignore[union-attr]
        "first_name": user.first_name,  # type: ignore[union-attr]
        "role": user.role.value,  # type: ignore[union-attr]
    }


def _build_profile_text(user: object) -> str:
    """Build profile text from user object."""
    profile_values = _get_user_profile_values(user)
    return "\n".join([
        "<b>Профиль</b>",
        "",
        f"Имя: {profile_values['first_name']} {profile_values['last_name']}",
        f"Роль: {profile_values['role']}",
        f"Телефон: {profile_values['phone']}",
        f"Email: {profile_values['email']}",
        f"Должность: {profile_values['position']}",
    ])


@profile_router.message(Command("profile"))
async def cmd_profile(message: types.Message) -> None:
    """Handle /profile command."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if not user:
            await message.answer(
                "Сначала зарегистрируйтесь командой /start",
            )
            return
        profile_text = _build_profile_text(user)
        await message.answer(
            profile_text, reply_markup=get_profile_keyboard(),
        )


@profile_router.callback_query(
    lambda callback: callback.data == "profile",
)
async def show_profile(callback: types.CallbackQuery) -> None:
    """Show user profile."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if not user:
            await callback.answer(
                "Сначала зарегистрируйтесь", show_alert=True,
            )
            return
        profile_text = _build_profile_text(user)
        await callback.message.edit_text(
            profile_text, reply_markup=get_profile_keyboard(),
        )


@profile_router.callback_query(
    lambda callback: callback.data == "edit_profile",
)
async def edit_profile(callback: types.CallbackQuery) -> None:
    """Edit user profile."""
    await callback.message.edit_text(
        "Выберите поле для редактирования:",
        reply_markup=get_edit_profile_keyboard(),
    )


@profile_router.callback_query(
    lambda callback: callback.data.startswith("edit_"),
)
async def edit_field(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Edit specific profile field."""
    field = callback.data.split("_")[1]
    await state.update_data(edit_field=field)
    field_label = _get_field_label(field)
    await callback.message.edit_text(
        f"Введите новое значение для поля '{field_label}':",
    )
    await state.set_state(ProfileEdit.field_value)


@profile_router.message(ProfileEdit.field_value)
async def save_profile_value(
    message: types.Message, state: FSMContext,
) -> None:
    """Save profile field value."""
    edit_data = await state.get_data()
    field = edit_data.get("edit_field")
    async for session in get_session():
        update_params: UserUpdateParams = {
            field: message.text,
        }  # type: ignore[arg-type]
        await update_user_profile(
            session, message.from_user.id, params=update_params,
        )
    await message.answer(
        "Профиль обновлен!",
        reply_markup=get_back_keyboard("profile"),
    )
    await state.clear()
