"""Geocoding module using Yandex Geocoder API."""

import httpx

from bot.config import YANDEX_GEOCODER_API_KEY

POINT_LEN = 2


def _extract_coordinates(data: dict) -> tuple[float, float] | None:
    """Extract coordinates from geocoding response data."""
    feature = (
        data.get("response", {})
        .get("GeoObjectCollection", {})
        .get("featureMember", [])
    )
    if not feature:
        return None
    point = (
        feature[0]
        .get("GeoObject", {})
        .get("Point", {})
        .get("pos", "")
        .split()
    )
    if len(point) == POINT_LEN:
        return float(point[0]), float(point[1])
    return None


async def geocode_address(address: str) -> tuple[float, float] | None:
    """Geocode address using Yandex Geocoder API.

    Returns tuple of (longitude, latitude) or None if not found.
    """
    if not YANDEX_GEOCODER_API_KEY:
        return None

    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_GEOCODER_API_KEY,
        "geocode": address,
        "format": "json",
        "lang": "ru_RU",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return _extract_coordinates(data)
        except (httpx.HTTPError, ValueError, KeyError):
            return None

    return None


def _extract_name(data: dict) -> str | None:
    """Extract name from reverse geocoding response."""
    feature = (
        data.get("response", {})
        .get("GeoObjectCollection", {})
        .get("featureMember", [])
    )
    if feature:
        name = feature[0].get("GeoObject", {}).get("name", "")
        return name or None
    return None


async def reverse_geocode(
    longitude: float,
    latitude: float,
) -> str | None:
    """Reverse geocode coordinates using Yandex Geocoder API.

    Returns address string or None if not found.
    """
    if not YANDEX_GEOCODER_API_KEY:
        return None

    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        "apikey": YANDEX_GEOCODER_API_KEY,
        "geocode": f"{longitude},{latitude}",
        "format": "json",
        "lang": "ru_RU",
        "kind": "locality",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, params=params, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            return _extract_name(data)
        except (httpx.HTTPError, ValueError, KeyError):
            return None

    return None
