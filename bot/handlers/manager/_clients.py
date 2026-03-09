"""Client handlers for manager."""

import logging
from typing import TYPE_CHECKING

from aiogram import F, Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.client_company_crud import (
    CompanyCreateParams,
    create_company,
    get_all_companies,
)
from bot.database.database import get_session
from bot.keyboards.menus import get_clients_keyboard
from bot.states.states import CompanyCreation

logger = logging.getLogger(__name__)

clients_router = Router()

# Skip option text
_SKIP_OPTION = "пропустить"

# Field keys for company (immutable tuple)
_COMPANY_FIELDS = ("inn", "kpp", "address", "phone", "email", "website")


def _build_company_params(company_data: dict) -> CompanyCreateParams:
    """Build company creation params."""
    company_params: CompanyCreateParams = {"name": company_data["name"]}
    for field_key in _COMPANY_FIELDS:
        if company_data.get(field_key):
            company_params[field_key] = company_data[
                field_key
            ]  # type: ignore[literal-required]
    return company_params


@clients_router.callback_query(F.data == "clients")
async def clients(callback: types.CallbackQuery) -> None:
    """Show clients list."""
    async for session in get_session():
        companies = await get_all_companies(session)
        await callback.message.edit_text(
            "Клиенты:", reply_markup=get_clients_keyboard(companies),
        )


@clients_router.callback_query(F.data == "add_client")
async def add_client_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start adding client."""
    await callback.message.edit_text(
        "Добавление клиента.\nНазвание компании:",
    )
    await state.set_state(CompanyCreation.name)


@clients_router.message(CompanyCreation.name)
async def company_name(message: types.Message, state: FSMContext) -> None:
    """Process company name."""
    await state.update_data(name=message.text)
    await message.answer(f"ИНН (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.inn)


@clients_router.message(CompanyCreation.inn)
async def company_inn(message: types.Message, state: FSMContext) -> None:
    """Process company INN."""
    inn_val: str | None = None
    if message.text != _SKIP_OPTION:
        inn_val = message.text
    await state.update_data(inn=inn_val)
    await message.answer(f"КПП (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.kpp)


@clients_router.message(CompanyCreation.kpp)
async def company_kpp(message: types.Message, state: FSMContext) -> None:
    """Process company KPP."""
    kpp_val: str | None = None
    if message.text != _SKIP_OPTION:
        kpp_val = message.text
    await state.update_data(kpp=kpp_val)
    await message.answer(f"Адрес (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.address)


@clients_router.message(CompanyCreation.address)
async def company_address(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company address."""
    address_val: str | None = None
    if message.text != _SKIP_OPTION:
        address_val = message.text
    await state.update_data(address=address_val)
    await message.answer(f"Телефон (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.phone)


@clients_router.message(CompanyCreation.phone)
async def company_phone(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company phone."""
    phone_val: str | None = None
    if message.text != _SKIP_OPTION:
        phone_val = message.text
    await state.update_data(phone=phone_val)
    await message.answer(f"Email (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.email)


@clients_router.message(CompanyCreation.email)
async def company_email(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company email."""
    email_val: str | None = None
    if message.text != _SKIP_OPTION:
        email_val = message.text
    await state.update_data(email=email_val)
    await message.answer(f"Сайт (или '{_SKIP_OPTION}'):")
    await state.set_state(CompanyCreation.website)


@clients_router.message(CompanyCreation.website)
async def company_website(
    message: types.Message, state: FSMContext,
) -> None:
    """Process company website and create company."""
    website_val: str | None = None
    if message.text != _SKIP_OPTION:
        website_val = message.text
    await state.update_data(website=website_val)
    company_data = await state.get_data()
    async for session in get_session():
        company_params = _build_company_params(company_data)
        await create_company(session=session, params=company_params)
    await message.answer("Клиент добавлен!")
    await state.clear()
