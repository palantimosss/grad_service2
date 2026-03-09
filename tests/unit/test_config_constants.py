"""Tests for config module - constants tests."""

from bot.config import (
    ADMIN_IDS,
    BASE_DIR,
    BOT_TOKEN,
    DATA_DIR,
    DATABASE_PATH,
    FILES_DIR,
    HOUR_SECONDS,
)

# Constants for test assertions
_EXPECTED_HOUR_SECONDS = 3600


class TestConfigConstants:
    """Tests for config constants."""

    def test_config_constants(self) -> None:
        """Test config constants."""
        assert HOUR_SECONDS == _EXPECTED_HOUR_SECONDS

    def test_base_constants(self) -> None:
        """Test base directory constants."""
        assert BASE_DIR is not None
        assert DATA_DIR is not None
        assert DATABASE_PATH is not None
        assert FILES_DIR is not None

    def test_bot_token(self) -> None:
        """Test bot token config."""
        assert isinstance(BOT_TOKEN, str)

    def test_admin_ids(self) -> None:
        """Test admin IDs config."""
        assert isinstance(ADMIN_IDS, list)
