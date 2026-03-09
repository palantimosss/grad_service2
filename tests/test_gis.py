"""Tests for GIS module."""

from unittest.mock import patch

import pytest

from bot.gis.geocoding import (
    _extract_coordinates,
    _extract_name,
    geocode_address,
    reverse_geocode,
)
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

    def test_get_zone_polygons_with_features(self) -> None:
        """Test getting polygons from data with features."""
        zone_data = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [[[30.0, 60.0], [31.0, 60.0]]],
                        "type": "Polygon",
                    },
                },
            ],
        }
        polygons = get_zone_polygons(zone_data)
        assert len(polygons) == 1


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

    def test_point_in_zone_with_polygon(self) -> None:
        """Test point check with polygon data."""
        zone_data = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [[
                            [30.0, 60.0], [31.0, 60.0],
                            [31.0, 61.0], [30.0, 61.0],
                            [30.0, 60.0],
                        ]],
                        "type": "Polygon",
                    },
                },
            ],
        }
        # Point inside polygon
        result = is_point_in_zone(30.5, 60.5, zone_data)
        assert result is True

    def test_point_outside_zone(self) -> None:
        """Test point outside zone."""
        zone_data = {
            "features": [
                {
                    "geometry": {
                        "coordinates": [[
                            [30.0, 60.0], [31.0, 60.0],
                            [31.0, 61.0], [30.0, 61.0],
                            [30.0, 60.0],
                        ]],
                        "type": "Polygon",
                    },
                },
            ],
        }
        # Point outside polygon
        result = is_point_in_zone(35.0, 65.0, zone_data)
        assert result is False


@pytest.mark.asyncio
class TestGeocoding:
    """Tests for geocoding module."""

    async def test_geocode_empty_api_key(self) -> None:
        """Test geocoding with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            result = await geocode_address("Test address")
            assert result is None

    async def test_reverse_geocode_empty_api_key(self) -> None:
        """Test reverse geocoding with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            result = await reverse_geocode(30.0, 60.0)
            assert result is None

    async def test_extract_coordinates_empty(self) -> None:
        """Test _extract_coordinates with empty data."""
        result = _extract_coordinates({})
        assert result is None

    async def test_extract_coordinates_success(self) -> None:
        """Test _extract_coordinates with valid data."""
        data = {
            "response": {
                "GeoObjectCollection": {
                    "featureMember": [
                        {
                            "GeoObject": {
                                "Point": {"pos": "30.3158 59.9391"},
                            },
                        },
                    ],
                },
            },
        }
        result = _extract_coordinates(data)
        assert result == (30.3158, 59.9391)

    async def test_extract_name_empty(self) -> None:
        """Test _extract_name with empty data."""
        result = _extract_name({})
        assert result is None

    async def test_extract_name_success(self) -> None:
        """Test _extract_name with valid data."""
        data = {
            "response": {
                "GeoObjectCollection": {
                    "featureMember": [
                        {
                            "GeoObject": {
                                "name": "Moscow",
                            },
                        },
                    ],
                },
            },
        }
        result = _extract_name(data)
        assert result == "Moscow"


@pytest.mark.asyncio
class TestGISServer:
    """Tests for GIS server."""

    async def test_check_address_empty_api_key(self) -> None:
        """Test address check with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            result = await check_meeting_address("Test address")
            assert result.success is False
            assert result.coordinates is None
