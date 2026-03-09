"""Tests for bot factory and dispatcher factory."""

from unittest.mock import MagicMock, patch

from bot.services.bot_factory import create_bot
from bot.services.dispatcher_factory import create_dispatcher


class TestBotFactory:
    """Tests for bot factory."""

    async def test_create_bot(self) -> None:
        """Test bot creation."""
        with patch("bot.services.bot_factory.Bot") as mock_bot:
            mock_bot_instance = MagicMock()
            mock_bot.return_value = mock_bot_instance
            bot = create_bot()
            assert bot is not None


class TestDispatcherFactory:
    """Tests for dispatcher factory."""

    def test_create_dispatcher(self) -> None:
        """Test dispatcher creation."""
        dispatcher = create_dispatcher()
        assert dispatcher is not None
        assert hasattr(dispatcher, "update")
