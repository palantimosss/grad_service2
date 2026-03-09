"""Zone checker for GIS module."""

from shapely.geometry import Point, Polygon

from bot.gis.zone_loader import get_zone_polygons, load_service_zone


def is_point_in_zone(
    longitude: float, latitude: float, zone_data: dict | None = None,
) -> bool:
    """Check if point is inside service zone.

    Args:
        longitude: Point longitude.
        latitude: Point latitude.
        zone_data: Zone GeoJSON data (loaded if None).

    Returns:
        True if point is inside zone, False otherwise.

    """
    if zone_data is None:
        zone_data = load_service_zone()

    if zone_data is None:
        return False

    point = Point(longitude, latitude)
    polygons = get_zone_polygons(zone_data)

    for polygon_coords in polygons:
        polygon = Polygon(polygon_coords)
        if polygon.contains(point):
            return True

    return False


def check_address_in_zone(
    longitude: float, latitude: float, zone_data: dict | None = None,
) -> tuple[bool, str]:
    """Check if address coordinates are in service zone.

    Returns:
        Tuple of (is_inside, message).

    """
    if is_point_in_zone(longitude, latitude, zone_data):
        return True, "Адрес находится в зоне обслуживания"

    return (
        False,
        "Адрес вне зоны обслуживания. Рекомендуется онлайн-встреча",
    )
