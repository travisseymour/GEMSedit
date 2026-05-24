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
        [left, top],  # top-left
        [left + width, top],  # top-right
        [left + width, top + height],  # bottom-right
        [left, top + height],  # bottom-left
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


def _point_in_polygon(point: Point, polygon: Polygon) -> bool:
    """
    Check if a point is inside a polygon using ray casting algorithm.

    Args:
        point: Point [x, y] to test
        polygon: List of [x, y] coordinate pairs defining the polygon

    Returns:
        True if point is inside the polygon
    """
    if len(polygon) < 3:
        return False

    x, y = point[0], point[1]
    n = len(polygon)
    inside = False

    j = n - 1
    for i in range(n):
        xi, yi = polygon[i][0], polygon[i][1]
        xj, yj = polygon[j][0], polygon[j][1]

        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i

    return inside


def _segments_intersect(p1: Point, p2: Point, p3: Point, p4: Point) -> bool:
    """
    Check if line segment (p1, p2) intersects with line segment (p3, p4).

    Uses the cross product method to determine intersection.
    """

    def ccw(a: Point, b: Point, c: Point) -> bool:
        """Check if three points are in counter-clockwise order."""
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])

    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def polygons_overlap(poly1: Polygon, poly2: Polygon) -> bool:
    """
    Check if two polygons overlap (intersect or one contains the other).

    Args:
        poly1: First polygon as list of [x, y] points
        poly2: Second polygon as list of [x, y] points

    Returns:
        True if the polygons overlap
    """
    if len(poly1) < 3 or len(poly2) < 3:
        return False

    # First, quick bounding box check
    bbox1 = points_to_bounding_rect(poly1)
    bbox2 = points_to_bounding_rect(poly2)

    # Bounding boxes: (left, top, width, height)
    if (
        bbox1[0] > bbox2[0] + bbox2[2]
        or bbox2[0] > bbox1[0] + bbox1[2]
        or bbox1[1] > bbox2[1] + bbox2[3]
        or bbox2[1] > bbox1[1] + bbox1[3]
    ):
        return False  # Bounding boxes don't overlap

    # Check if any edge of poly1 intersects any edge of poly2
    n1, n2 = len(poly1), len(poly2)
    for i in range(n1):
        p1, p2 = poly1[i], poly1[(i + 1) % n1]
        for j in range(n2):
            p3, p4 = poly2[j], poly2[(j + 1) % n2]
            if _segments_intersect(p1, p2, p3, p4):
                return True

    # Check if any vertex of poly1 is inside poly2
    for point in poly1:
        if _point_in_polygon(point, poly2):
            return True

    # Check if any vertex of poly2 is inside poly1
    for point in poly2:
        if _point_in_polygon(point, poly1):
            return True

    return False
