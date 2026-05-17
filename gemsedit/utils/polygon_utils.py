"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2021-2026 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import json
from typing import TypeAlias

Point: TypeAlias = list[int]  # [x, y]
Polygon: TypeAlias = list[Point]  # [[x1,y1], [x2,y2], ...]


def rect_to_points(left: int, top: int, width: int, height: int) -> Polygon:
    """
    Convert rectangle bounds to a 4-point polygon (clockwise from top-left).

    Args:
        left: X coordinate of top-left corner
        top: Y coordinate of top-left corner
        width: Width of rectangle
        height: Height of rectangle

    Returns:
        List of 4 points, or empty list if dimensions are invalid
    """
    if width <= 0 or height <= 0:
        return []
    return [
        [left, top],                    # top-left
        [left + width, top],            # top-right
        [left + width, top + height],   # bottom-right
        [left, top + height],           # bottom-left
    ]


def points_to_bounding_rect(points: Polygon) -> tuple[int, int, int, int]:
    """
    Get the axis-aligned bounding rectangle for a polygon.

    Args:
        points: List of [x, y] coordinate pairs

    Returns:
        Tuple of (left, top, width, height), or (0, 0, 0, 0) if empty
    """
    if not points:
        return (0, 0, 0, 0)
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    left, top = min(xs), min(ys)
    right, bottom = max(xs), max(ys)
    return (left, top, right - left, bottom - top)


def points_to_json(points: Polygon) -> str:
    """
    Serialize polygon points to a JSON string.

    Args:
        points: List of [x, y] coordinate pairs

    Returns:
        JSON string representation
    """
    return json.dumps(points)


def json_to_points(json_str: str | None) -> Polygon:
    """
    Deserialize polygon points from a JSON string.

    Args:
        json_str: JSON string containing list of [x, y] pairs

    Returns:
        List of points, or empty list if invalid/empty
    """
    if not json_str:
        return []
    try:
        result = json.loads(json_str)
        if isinstance(result, list):
            return result
        return []
    except (json.JSONDecodeError, TypeError):
        return []


def is_point_near(p1: Point, p2: Point, threshold: int = 15) -> bool:
    """
    Check if two points are within a threshold distance of each other.

    Args:
        p1: First point [x, y]
        p2: Second point [x, y]
        threshold: Maximum distance in pixels

    Returns:
        True if points are within threshold distance
    """
    return abs(p1[0] - p2[0]) <= threshold and abs(p1[1] - p2[1]) <= threshold


def polygon_centroid(points: Polygon) -> Point:
    """
    Calculate the centroid (center of mass) of a polygon.

    Args:
        points: List of [x, y] coordinate pairs

    Returns:
        Centroid point [x, y], or [0, 0] if empty
    """
    if not points:
        return [0, 0]
    cx = sum(p[0] for p in points) // len(points)
    cy = sum(p[1] for p in points) // len(points)
    return [cx, cy]
