"""Tests for config module - deadline and API tests."""

from bot.config import (
    DEADLINE_MAX_HOURS,
    DEADLINE_MIN_HOURS,
    YANDEX_GEOCODER_API_KEY,
)

# Constants for test assertions
_EXPECTED_DEADLINE_MAX_HOURS = 25
_EXPECTED_DEADLINE_MIN_HOURS = 23


class TestConfigDeadlines:
    """Tests for config deadline and API settings."""

    def test_deadline_constants(self) -> None:
        """Test deadline constants."""
        assert DEADLINE_MIN_HOURS == _EXPECTED_DEADLINE_MIN_HOURS
        assert DEADLINE_MAX_HOURS == _EXPECTED_DEADLINE_MAX_HOURS

    def test_yandex_geocoder_api_key(self) -> None:
        """Test Yandex Geocoder API key config."""
        assert isinstance(YANDEX_GEOCODER_API_KEY, str)
