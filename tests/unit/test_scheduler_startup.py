"""Tests for scheduler and startup/shutdown hooks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from bot.services.routers import register_routers
from bot.services.scheduler import check_deadlines, create_scheduler
from bot.services.startup import on_shutdown, on_startup


@pytest.mark.asyncio
class TestScheduler:
    """Tests for scheduler."""

    def test_create_scheduler(self) -> None:
        """Test scheduler creation."""
        scheduler = create_scheduler()
        assert scheduler is not None

    async def test_check_deadlines(self) -> None:
        """Test check deadlines function."""
        await check_deadlines()


@pytest.mark.asyncio
class TestStartup:
    """Tests for startup/shutdown hooks."""

    async def test_on_startup(self) -> None:
        """Test on_startup hook."""
        mock_bot = AsyncMock()
        mock_bot.get_me = AsyncMock(
            return_value=MagicMock(username="test_bot"),
        )

        with patch(
            "bot.services.startup.create_tables",
            new_callable=AsyncMock,
        ):
            await on_startup(mock_bot)
            mock_bot.get_me.assert_called_once()

    async def test_on_shutdown(self) -> None:
        """Test on_shutdown hook."""
        mock_bot = AsyncMock()
        mock_bot.session.close = AsyncMock()

        await on_shutdown(mock_bot)
        mock_bot.session.close.assert_called_once()


class TestRouters:
    """Tests for routers registration."""

    def test_register_routers(self) -> None:
        """Test routers registration."""
        mock_dispatcher = MagicMock()
        mock_dispatcher.include_routers = MagicMock()

        register_routers(mock_dispatcher)
        mock_dispatcher.include_routers.assert_called_once()
