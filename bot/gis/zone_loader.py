"""Zone loader for GIS module."""

import json
from typing import Any

from bot.config import DATA_DIR


def load_service_zone() -> dict[str, Any] | None:
    """Load service zone from GeoJSON file."""
    zone_path = DATA_DIR / "service_zone.geojson"
    if not zone_path.exists():
        return None

    with zone_path.open(encoding="utf-8") as f:
        return json.load(f)


def get_zone_polygons(
    zone_data: dict[str, Any],
) -> list[list[tuple[float, float]]]:
    """Extract polygons from zone data."""
    polygons: list[list[tuple[float, float]]] = []
    features = zone_data.get("features", [])

    for feature in features:
        geometry = feature.get("geometry", {})
        geom_type = geometry.get("type")
        coords = geometry.get("coordinates", [])

        if geom_type == "Polygon":
            polygons.append(coords[0])
        elif geom_type == "MultiPolygon":
            polygons.extend(polygon_coords[0] for polygon_coords in coords)

    return polygons
