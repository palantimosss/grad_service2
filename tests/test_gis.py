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

# Test constants
TEST_LONGITUDE = 30.0
TEST_LATITUDE = 60.0
TEST_LONGITUDE_SPB = 30.3158
TEST_LATITUDE_SPB = 59.9391
TEST_LONGITUDE_INSIDE = 30.5
TEST_LATITUDE_INSIDE = 60.5
TEST_LONGITUDE_OUTSIDE = 35.0
TEST_LATITUDE_OUTSIDE = 65.0
TEST_DURATION = 30.0

# Feature key constant
_FEATURES_KEY = "features"


class TestZoneLoader:
    """Tests for zone loader."""

    def test_load_service_zone_missing_file(self) -> None:
        """Test loading missing zone file."""
        zone = load_service_zone()
        assert zone is None or isinstance(zone, dict)

    def test_get_zone_polygons_empty(self) -> None:
        """Test getting polygons from empty data."""
        polygons = get_zone_polygons({_FEATURES_KEY: []})
        assert polygons == []

    def test_get_zone_polygons_with_features(self) -> None:
        """Test getting polygons from data with features."""
        zone_data = {
            _FEATURES_KEY: [
                {
                    "geometry": {
                        "coordinates": [[
                            [TEST_LONGITUDE, TEST_LATITUDE],
                            [31.0, TEST_LATITUDE],
                        ]],
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
        is_inside = is_point_in_zone(
            TEST_LONGITUDE, TEST_LATITUDE, {_FEATURES_KEY: []},
        )
        assert is_inside is False

    def test_point_coordinates(self) -> None:
        """Test point coordinates format."""
        is_inside = is_point_in_zone(
            TEST_LONGITUDE_SPB, TEST_LATITUDE_SPB, {_FEATURES_KEY: []},
        )
        assert isinstance(is_inside, bool)

    def test_point_in_zone_with_polygon(self) -> None:
        """Test point check with polygon data."""
        zone_data = {
            _FEATURES_KEY: [
                {
                    "geometry": {
                        "coordinates": [[
                            [TEST_LONGITUDE, TEST_LATITUDE],
                            [31.0, TEST_LATITUDE],
                            [31.0, 61.0],
                            [TEST_LONGITUDE, 61.0],
                            [TEST_LONGITUDE, TEST_LATITUDE],
                        ]],
                        "type": "Polygon",
                    },
                },
            ],
        }
        # Point inside polygon
        is_inside = is_point_in_zone(
            TEST_LONGITUDE_INSIDE, TEST_LATITUDE_INSIDE, zone_data,
        )
        assert is_inside is True

    def test_point_outside_zone(self) -> None:
        """Test point outside zone."""
        zone_data = {
            _FEATURES_KEY: [
                {
                    "geometry": {
                        "coordinates": [[
                            [TEST_LONGITUDE, TEST_LATITUDE],
                            [31.0, TEST_LATITUDE],
                            [31.0, 61.0],
                            [TEST_LONGITUDE, 61.0],
                            [TEST_LONGITUDE, TEST_LATITUDE],
                        ]],
                        "type": "Polygon",
                    },
                },
            ],
        }
        # Point outside polygon
        is_inside = is_point_in_zone(
            TEST_LONGITUDE_OUTSIDE, TEST_LATITUDE_OUTSIDE, zone_data,
        )
        assert is_inside is False


@pytest.mark.asyncio
class TestGeocoding:
    """Tests for geocoding module."""

    async def test_geocode_empty_api_key(self) -> None:
        """Test geocoding with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            coordinates = await geocode_address("Test address")
            assert coordinates is None

    async def test_reverse_geocode_empty_api_key(self) -> None:
        """Test reverse geocoding with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            address = await reverse_geocode(TEST_LONGITUDE, TEST_LATITUDE)
            assert address is None

    async def test_extract_coordinates_empty(self) -> None:
        """Test _extract_coordinates with empty data."""
        coordinates = _extract_coordinates({})
        assert coordinates is None

    async def test_extract_coordinates_success(self) -> None:
        """Test _extract_coordinates with valid data."""
        response_data = {
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
        coordinates = _extract_coordinates(response_data)
        assert coordinates == (TEST_LONGITUDE_SPB, TEST_LATITUDE_SPB)

    async def test_extract_name_empty(self) -> None:
        """Test _extract_name with empty data."""
        name = _extract_name({})
        assert name is None

    async def test_extract_name_success(self) -> None:
        """Test _extract_name with valid data."""
        response_data = {
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
        name = _extract_name(response_data)
        assert name == "Moscow"


@pytest.mark.asyncio
class TestGISServer:
    """Tests for GIS server."""

    async def test_check_address_empty_api_key(self) -> None:
        """Test address check with empty API key."""
        with patch("bot.gis.geocoding.YANDEX_GEOCODER_API_KEY", ""):
            check_result = await check_meeting_address("Test address")
            assert check_result.success is False
            assert check_result.coordinates is None
