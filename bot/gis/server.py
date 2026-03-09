"""GIS server module for address validation."""

from typing import NamedTuple

from bot.gis.geocoding import geocode_address
from bot.gis.zone_checker import check_address_in_zone, load_service_zone


class GISCheckResult(NamedTuple):
    """GIS check result."""

    success: bool
    coordinates: tuple[float, float] | None
    inside_zone: bool
    message: str


def _build_error_result(message: str) -> GISCheckResult:
    """Build error result."""
    return GISCheckResult(
        success=False,
        coordinates=None,
        inside_zone=False,
        message=message,
    )


def _build_success_result(
    coordinates: tuple[float, float],
    *,
    is_inside: bool,
    message: str,
) -> GISCheckResult:
    """Build success result."""
    return GISCheckResult(
        success=True,
        coordinates=coordinates,
        inside_zone=is_inside,
        message=message,
    )


async def check_meeting_address(
    address: str,
) -> GISCheckResult:
    """Check if meeting address is valid and in service zone.

    Args:
        address: Address string to check.

    Returns:
        GISCheckResult with check outcome.

    """
    coordinates = await geocode_address(address)

    if coordinates is None:
        return _build_error_result(
            "Не удалось определить координаты адреса",
        )

    return _check_coordinates_in_zone(coordinates)


def _check_coordinates_in_zone(
    coordinates: tuple[float, float],
) -> GISCheckResult:
    """Check if coordinates are inside service zone."""
    longitude, latitude = coordinates
    zone_data = load_service_zone()
    is_inside, message = check_address_in_zone(
        longitude, latitude, zone_data,
    )
    return _build_success_result(coordinates, is_inside, message)
