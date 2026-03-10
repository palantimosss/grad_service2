"""Zone loader for GIS module."""

from __future__ import annotations

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


def _extract_feature_polygons(feature: dict[str, Any]) -> MultiPolygonCoords:
    """Extract polygons from a single feature."""
    polygons: MultiPolygonCoords = []
    geometry = feature.get("geometry", {})
    geom_type = geometry.get("type")
    coordinates = geometry.get("coordinates", [])

    if geom_type == "Polygon":
        polygons.append(coordinates[0])
    elif geom_type == "MultiPolygon":
        for polygon_coords in coordinates:
            polygons.append(polygon_coords[0])

    return polygons


def get_zone_polygons(
    zone_data: dict[str, Any],
) -> MultiPolygonCoords:
    """Extract polygons from zone data."""
    polygons: MultiPolygonCoords = []
    features = zone_data.get("features", [])

    for feature in features:
        feature_polygons = _extract_feature_polygons(feature)
        polygons.extend(feature_polygons)

    return polygons
