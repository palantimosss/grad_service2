"""Common handlers: registration, profile, help."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types
from aiogram.filters import Command, CommandStart

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.user_crud import (
    UserCreateParams,
    UserUpdateParams,
    create_user,
    get_user_by_telegram_id,
    update_user_profile,
)
from bot.database.database import get_session
from bot.database.models.enums import UserRole
from bot.keyboards.menus import (
    get_back_keyboard,
    get_edit_profile_keyboard,
    get_main_menu_keyboard,
    get_profile_keyboard,
    get_role_keyboard,
)
from bot.states.states import ProfileEdit, UserRegistration

logger = logging.getLogger(__name__)

common_router = Router()

# Field name mappings for profile editing (immutable tuple)
_FIELD_NAMES = (
    ("phone", "телефон"),
    ("email", "email"),
    ("position", "должность"),
)

# Field keys
_PHONE_KEY = "phone"
_EMAIL_KEY = "email"
_POSITION_KEY = "position"

HELP_TEXT = (
    "<b>Grad Service - Управление проектами</b>\n\n"
    "Команды:\n"
    "/start - Регистрация\n"
    "/menu - Главное меню\n"
    "/help - Эта справка\n"
    "/profile - Мой профиль\n\n"
    "Для помощи обратитесь к руководителю проекта."
)


def _get_field_label(field_key: str) -> str:
    """Get field label from field key."""
    for key, label in _FIELD_NAMES:
        if key == field_key:
            return label
    return field_key


def _build_profile_text(user: object) -> str:
    """Build profile text from user object."""
    last_name = user.last_name or ""  # type: ignore[union-attr]
    phone_val = user.phone or "Не указан"  # type: ignore[union-attr]
    email_val = user.email or "Не указан"  # type: ignore[union-attr]
    position_val = user.position or "Не указана"  # type: ignore[union-attr]
    first_name = user.first_name  # type: ignore[union-attr]
    role_val = user.role.value  # type: ignore[union-attr]
    return "\n".join([
        "<b>Профиль</b>",
        "",
        f"Имя: {first_name} {last_name}",
        f"Роль: {role_val}",
        f"Телефон: {phone_val}",
        f"Email: {email_val}",
        f"Должность: {position_val}",
    ])


def _get_update_params(
    profile_data: dict, position_val: str,
) -> UserUpdateParams:
    """Get user update params from data."""
    update_params: UserUpdateParams = {}
    if profile_data.get(_PHONE_KEY):
        update_params[_PHONE_KEY] = profile_data[_PHONE_KEY]
    if profile_data.get(_EMAIL_KEY):
        update_params[_EMAIL_KEY] = profile_data[_EMAIL_KEY]
    if position_val and position_val != "пропустить":
        update_params[_POSITION_KEY] = position_val
    return update_params


@common_router.message(CommandStart())
async def cmd_start(
    message: types.Message, state: FSMContext,
) -> None:
    """Handle /start command."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        if user:
            await message.answer(
                f"С возвращением, {user.first_name}!",
                reply_markup=get_main_menu_keyboard(user.role),
            )
            return
        await message.answer(
            "Добро пожаловать в Grad Service!\nВыберите вашу роль:",
            reply_markup=get_role_keyboard(),
        )
        await state.set_state(UserRegistration.role)


@common_router.callback_query(F.data.startswith("role_"))
async def process_role(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Process role selection."""
    role_str = callback.data.split("_")[1]
    role = UserRole(role_str)
    await state.update_data(role=role)
    await callback.message.edit_text(
        f"Вы выбрали: {role.value}\nВведите ваш телефон:",
    )
    await state.set_state(UserRegistration.phone)


@common_router.message(UserRegistration.phone)
async def process_phone(
    message: types.Message, state: FSMContext,
) -> None:
    """Process phone input."""
    phone = message.text
    await state.update_data(phone=phone)
    await message.answer("Введите ваш email:")
    await state.set_state(UserRegistration.email)


@common_router.message(UserRegistration.email)
async def process_email(
    message: types.Message, state: FSMContext,
) -> None:
    """Process email input."""
    email = message.text
    await state.update_data(email=email)
    await message.answer(
        "Введите вашу должность "
        "(для клиентов можно пропустить):",
    )
    await state.set_state(UserRegistration.position)


@common_router.message(UserRegistration.position)
async def process_position(
    message: types.Message, state: FSMContext,
) -> None:
    """Process position input."""
    position_val = message.text
    await state.update_data(position=position_val)
    reg_data = await state.get_data()
    role = reg_data.get("role", UserRole.CLIENT)
    async for session in get_session():
        await _register_user(session, message, reg_data, role)
    await message.answer(
        "Регистрация завершена!",
        reply_markup=get_main_menu_keyboard(role),
    )
    await state.clear()


async def _register_user(
    session: object,
    message: types.Message,
    reg_data: dict,
    role: UserRole,
) -> None:
    """Register user in database."""
    create_params: UserCreateParams = {
        "telegram_id": message.from_user.id,
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name,
        "role": role,
    }
    await create_user(session=session, params=create_params)
    update_params = _get_update_params(reg_data, reg_data.get("position", ""))
    if update_params:
        await update_user_profile(
            session, message.from_user.id, params=update_params,
        )


@common_router.message(Command("menu"))
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


@common_router.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    """Handle /help command."""
    await message.answer(HELP_TEXT)


@common_router.message(Command("profile"))
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


@common_router.callback_query(F.data == "profile")
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


@common_router.callback_query(F.data == "edit_profile")
async def edit_profile(callback: types.CallbackQuery) -> None:
    """Edit user profile."""
    await callback.message.edit_text(
        "Выберите поле для редактирования:",
        reply_markup=get_edit_profile_keyboard(),
    )


@common_router.callback_query(F.data.startswith("edit_"))
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


@common_router.message(ProfileEdit.field_value)
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


@common_router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery) -> None:
    """Return to main menu."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, callback.from_user.id)
        if user:
            await callback.message.edit_text(
                "Главное меню:",
                reply_markup=get_main_menu_keyboard(user.role),
            )


@common_router.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery) -> None:
    """Return to profile."""
    await cmd_profile(callback.message)


@common_router.callback_query(F.data == "cancel")
async def cancel_action(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Cancel current action."""
    await state.clear()
    await callback.message.edit_text("Действие отменено.")
    await cmd_menu(callback.message)
