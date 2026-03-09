"""Tests for GIS module."""

import pytest

from bot.gis.geocoding import geocode_address, reverse_geocode
from bot.gis.server import check_meeting_address
from bot.gis.zone_checker import is_point_in_zone
from bot.gis.zone_loader import get_zone_polygons, load_service_zone


class TestZoneLoader:
    """Tests for zone loader."""

    def test_load_service_zone_missing_file(self) -> None:
        """Test loading missing zone file."""
        zone = load_service_zone()
        assert zone is None or isinstance(zone, dict)

    def test_get_zone_polygons_empty(self) -> None:
        """Test getting polygons from empty data."""
        polygons = get_zone_polygons({"features": []})
        assert polygons == []


class TestZoneChecker:
    """Tests for zone checker."""

    def test_point_in_zone_empty_data(self) -> None:
        """Test point check with empty zone data."""
        result = is_point_in_zone(30.0, 60.0, {"features": []})
        assert result is False

    def test_point_coordinates(self) -> None:
        """Test point coordinates format."""
        result = is_point_in_zone(30.3158, 59.9391, {"features": []})
        assert isinstance(result, bool)


@pytest.mark.asyncio
class TestGeocoding:
    """Tests for geocoding module."""

    async def test_geocode_empty_api_key(self) -> None:
        """Test geocoding with empty API key."""
        result = await geocode_address("Test address")
        assert result is None

    async def test_reverse_geocode_empty_api_key(self) -> None:
        """Test reverse geocoding with empty API key."""
        result = await reverse_geocode(30.0, 60.0)
        assert result is None


@pytest.mark.asyncio
class TestGISServer:
    """Tests for GIS server."""

    async def test_check_address_empty_api_key(self) -> None:
        """Test address check with empty API key."""
        result = await check_meeting_address("Test address")
        assert result.success is False
        assert result.coordinates is None
