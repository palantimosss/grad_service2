"""Statistics handlers for manager."""

import logging

from aiogram import F, Router, types

from bot.database.crud_modules.statistics_crud import (
    get_projects_count_by_status,
    get_tasks_count_by_status,
    get_users_count_by_role,
)
from bot.database.database import get_session
from bot.keyboards.menus import get_back_keyboard

logger = logging.getLogger(__name__)

stats_router = Router()


def _build_stats_text(
    projects_stats: dict,
    tasks_stats: dict,
    users_stats: dict,
) -> str:
    """Build statistics text."""
    lines = ["<b>Статистика</b>", "", "<b>Проекты:</b>"]
    for status, count in projects_stats.items():
        lines.append(f"  {status.value}: {count}")
    lines.append("")
    lines.append("<b>Задачи:</b>")
    for status, count in tasks_stats.items():
        lines.append(f"  {status.value}: {count}")
    lines.append("")
    lines.append("<b>Пользователи:</b>")
    for role, count in users_stats.items():
        lines.append(f"  {role.value}: {count}")
    return "\n".join(lines)


@stats_router.callback_query(F.data == "statistics")
async def statistics(callback: types.CallbackQuery) -> None:
    """Show statistics."""
    async for session in get_session():
        p_stats = await get_projects_count_by_status(session)
        t_stats = await get_tasks_count_by_status(session)
        u_stats = await get_users_count_by_role(session)
        text = _build_stats_text(p_stats, t_stats, u_stats)
        await callback.message.edit_text(
            text, reply_markup=get_back_keyboard(),
        )
