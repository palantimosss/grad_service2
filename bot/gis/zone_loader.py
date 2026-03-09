"""Zone loader for GIS module."""

import json
from typing import Any

from bot.config import DATA_DIR

# Type aliases for complex annotations
PolygonCoords = list[tuple[float, float]]
MultiPolygonCoords = list[list[tuple[float, float]]]


def load_service_zone() -> dict[str, Any] | None:
    """Load service zone from GeoJSON file."""
    zone_path = DATA_DIR / "service_zone.geojson"
    if not zone_path.exists():
        return None

    with zone_path.open(encoding="utf-8") as zone_file:
        return json.load(zone_file)


def get_zone_polygons(
    zone_data: dict[str, Any],
) -> MultiPolygonCoords:
    """Extract polygons from zone data."""
    polygons: MultiPolygonCoords = []
    features = zone_data.get("features", [])

    for feature in features:
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        coordinates = geometry.get("coordinates", [])

        if geom_type == "Polygon":
            polygons.append(coordinates[0])
        elif geom_type == "MultiPolygon":
            for polygon_coords in coordinates:
                polygons.append(polygon_coords[0])

    return polygons
