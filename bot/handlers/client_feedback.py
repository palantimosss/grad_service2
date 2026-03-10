"""Client handlers: feedback."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from aiogram import Router, types

if TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

from bot.database.crud_modules.feedback_crud import (
    FeedbackCreateParams,
    create_feedback,
)
from bot.database.crud_modules.user_crud import get_user_by_telegram_id
from bot.database.database import get_session
from bot.keyboards.menus import get_back_keyboard
from bot.states.states import FeedbackCreation

logger = logging.getLogger(__name__)

client_feedback_router = Router()

_PROJECT_ID_KEY = "project_id"
_AUTHOR_ID_KEY = "author_id"


async def _create_feedback_in_db(
    session: object,
    feedback_data: dict,
) -> None:
    """Create feedback in database."""
    feedback_params: FeedbackCreateParams = {
        _PROJECT_ID_KEY: feedback_data[_PROJECT_ID_KEY],
        _AUTHOR_ID_KEY: feedback_data[_AUTHOR_ID_KEY],
        "message": feedback_data["message"],
        "rating": None,
    }
    await create_feedback(session=session, params=feedback_params)


@client_feedback_router.callback_query(
    lambda callback: callback.data.startswith("feedback_"),
)
async def feedback_start(
    callback: types.CallbackQuery, state: FSMContext,
) -> None:
    """Start feedback creation."""
    parts = callback.data.split("_")
    project_id = int(parts[1])
    await state.update_data(project_id=project_id)
    await callback.message.edit_text("Введите ваш отзыв о проекте:")
    await state.set_state(FeedbackCreation.message)


@client_feedback_router.message(FeedbackCreation.message)
async def feedback_message(
    message: types.Message, state: FSMContext,
) -> None:
    """Process feedback message."""
    state_data = await state.get_data()
    project_id = state_data.get("project_id")
    await _process_feedback_creation(message, state, project_id)


async def _process_feedback_creation(
    message: types.Message,
    state: FSMContext,
    project_id: int | None,
) -> None:
    """Process feedback creation and save to database."""
    async for session in get_session():
        user = await get_user_by_telegram_id(session, message.from_user.id)
        await _create_feedback_in_db(
            session,
            {
                "project_id": project_id,
                "author_id": user.id,
                "message": message.text,
            },
        )
    await message.answer(
        "Спасибо за ваш отзыв!",
        reply_markup=get_back_keyboard(f"project_{project_id}"),
    )
    await state.clear()
