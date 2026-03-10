"""Geocoding module using Yandex Geocoder API."""

from __future__ import annotations

import httpx

from bot.config import YANDEX_GEOCODER_API_KEY

POINT_LEN = 2
REQUEST_TIMEOUT = 10.0


def _extract_coordinates(response_data: dict) -> tuple[float, float] | None:
    """Extract coordinates from geocoding response data."""
    feature = (
        response_data.get("response", {})
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
    request_params = {
        "apikey": YANDEX_GEOCODER_API_KEY,
        "geocode": address,
        "format": "json",
        "lang": "ru_RU",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=request_params, timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
            return _extract_coordinates(response_data)
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def _extract_name(response_data: dict) -> str | None:
    """Extract name from reverse geocoding response."""
    feature = (
        response_data.get("response", {})
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
    request_params = {
        "apikey": YANDEX_GEOCODER_API_KEY,
        "geocode": f"{longitude},{latitude}",
        "format": "json",
        "lang": "ru_RU",
        "kind": "locality",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url, params=request_params, timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            response_data = response.json()
            return _extract_name(response_data)
    except (httpx.HTTPError, ValueError, KeyError):
        return None
