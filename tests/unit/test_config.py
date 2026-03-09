"""Tests for config module - base constants."""

from bot.config import (
    ADMIN_IDS,
    BASE_DIR,
    BOT_TOKEN,
    DATA_DIR,
    DATABASE_PATH,
    DEADLINE_MAX_HOURS,
    DEADLINE_MIN_HOURS,
    FILES_DIR,
    HOUR_SECONDS,
    YANDEX_GEOCODER_API_KEY,
)

# Constants for test assertions
_EXPECTED_DEADLINE_MAX_HOURS = 25
_EXPECTED_DEADLINE_MIN_HOURS = 23
_EXPECTED_HOUR_SECONDS = 3600


class TestConfig:
    """Tests for config module."""

    def test_config_constants(self) -> None:
        """Test config constants."""
        assert HOUR_SECONDS == _EXPECTED_HOUR_SECONDS
        assert DEADLINE_MIN_HOURS == _EXPECTED_DEADLINE_MIN_HOURS
        assert DEADLINE_MAX_HOURS == _EXPECTED_DEADLINE_MAX_HOURS

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

    def test_yandex_geocoder_api_key(self) -> None:
        """Test Yandex Geocoder API key config."""
        assert isinstance(YANDEX_GEOCODER_API_KEY, str)
