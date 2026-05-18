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

import os

from PySide6 import QtCore, QtGui, QtSql, QtWidgets
from PySide6.QtCore import QPoint
from PySide6.QtWidgets import QApplication

import gemsedit
from gemsedit import log
from gemsedit.utils.polygon_utils import (
    is_point_near,
    json_to_points,
    polygon_centroid,
)


class ObjectSelect(QtWidgets.QDialog):
    def __init__(
        self,
        parent=None,
        current_view=None,
        current_obj=None,
        allow_selection=True,
        view_pic="Foreground",
        media_path=None,
    ):
        super().__init__(parent)
        self.current_view = current_view
        self.current_obj = current_obj
        self.allow_selection = allow_selection
        self.view_pic = view_pic
        self.media_path = media_path
        self.clicks_allowed = False
        self.other_objects = []  # List of (name, points_json, visible, takeable, draggable)
        self.bgPic = None
        self._result: list = []  # Result is now a list of [x, y] points
        self._keep_result = False

        # Polygon drawing state
        self.points: list[list[int]] = []  # Current polygon being drawn
        self.is_drawing = False  # True when actively placing points
        self.hover_point: list[int] | None = None  # Mouse position for preview
        self.close_threshold = 15  # Pixels to detect closing polygon
        self.shift_held = False  # For constrained drawing

        self.msg = "Press ENTER to close this window."
        self.msg_position = QPoint(20, 20)

        if self.allow_selection:
            self.msg = "Click to place polygon points. Double-click or click near start to close."
        else:
            self.msg = "Press ENTER to close."

        QtCore.QTimer.singleShot(1000, self.allow_clicks)  # Avoids ghost click from objects ui

    def allow_clicks(self):
        if self.allow_selection:
            self.clicks_allowed = True

    def showEvent(self, event):
        # Set bgPic
        if self.current_view is not None:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM views where Id = :viewid order by RowOrder")
            query.bindValue(":viewid", self.current_view)
            query.exec()
            if query.isActive():
                query.first()
                foreground = os.path.join(self.media_path, query.value(2))
                background = os.path.join(self.media_path, query.value(3))
                overlay = os.path.join(self.media_path, query.value(4))
                if self.view_pic == "Foreground" and os.path.isfile(foreground):
                    self.bgPic = foreground
                elif self.view_pic == "Background" and os.path.isfile(background):
                    self.bgPic = background
                elif self.view_pic == "Overlay" and os.path.isfile(overlay):
                    self.bgPic = overlay
                else:
                    log.error("Error in objects.showEvent(): viewpic is invalid or associated file is unreadable.")
                    return

        # Load Object Coordinates - now using Points column
        query = QtSql.QSqlQuery()
        query.prepare(
            "SELECT Id, Name, Points, Visible, Takeable, Draggable FROM objects WHERE Parent = :viewid ORDER BY RowOrder"
        )
        query.bindValue(":viewid", self.current_view)
        query.exec()
        if query.isActive():
            while query.next():
                _id = query.value(0)
                name = query.value(1)
                points_json = query.value(2) or "[]"
                visible = query.value(3)
                takeable = query.value(4)
                draggable = query.value(5)

                if _id == self.current_obj:
                    # Load current object's polygon
                    self.points = json_to_points(points_json)
                else:
                    self.other_objects.append((name, points_json, visible, takeable, draggable))

        super().showEvent(event)

    def closeEvent(self, event):
        if not self._keep_result:
            self._result = []
        else:
            # Only return valid polygons (3+ points)
            self._result = self.points.copy() if len(self.points) >= 3 else []
        self._keep_result = False
        super().closeEvent(event)

    def _is_near_first_point(self, pos: list[int]) -> bool:
        """Check if position is near the first point of the polygon."""
        if not self.points:
            return False
        return is_point_near(pos, self.points[0], self.close_threshold)

    def _constrain_point(self, pos: list[int]) -> list[int]:
        """Constrain point to horizontal or vertical from last point."""
        if not self.points:
            return pos
        last = self.points[-1]
        dx, dy = abs(pos[0] - last[0]), abs(pos[1] - last[1])
        if dx > dy:
            return [pos[0], last[1]]  # Horizontal
        else:
            return [last[0], pos[1]]  # Vertical

    def _close_polygon(self):
        """Finalize the current polygon."""
        self.is_drawing = False
        self.setMouseTracking(False)
        self.hover_point = None
        self.msg = "Polygon complete. Press ENTER to confirm, ESC to cancel, or click to start new polygon."
        self.update()

    def mousePressEvent(self, event):
        if not self.allow_selection or not self.clicks_allowed:
            return super().mousePressEvent(event)

        pos = [event.pos().x(), event.pos().y()]

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if not self.is_drawing:
                # Start new polygon
                self.points = [pos]
                self.is_drawing = True
                self.setMouseTracking(True)
                self.msg = "Click to add points. Double-click or click near start to close. Right-click to undo."
            else:
                # Check if closing polygon (click near first point)
                if len(self.points) >= 3 and self._is_near_first_point(pos):
                    self._close_polygon()
                else:
                    # Apply shift constraint if held
                    if self.shift_held and len(self.points) > 0:
                        pos = self._constrain_point(pos)
                    self.points.append(pos)
            self.update()

        elif event.button() == QtCore.Qt.MouseButton.RightButton:
            # Undo last point
            if self.is_drawing and len(self.points) > 1:
                self.points.pop()
                self.update()
            elif self.is_drawing and len(self.points) == 1:
                # Cancel drawing
                self.points = []
                self.is_drawing = False
                self.setMouseTracking(False)
                self.msg = "Click to start drawing polygon."
                self.update()

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self.allow_selection and self.is_drawing and len(self.points) >= 3:
            self._close_polygon()
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.allow_selection and self.is_drawing:
            pos = [event.pos().x(), event.pos().y()]
            if self.shift_held and len(self.points) > 0:
                pos = self._constrain_point(pos)
            self.hover_point = pos
            self.update()
        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        # setup painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        # draw image
        if self.bgPic:
            painter.drawPixmap(0, 0, QtGui.QPixmap(self.bgPic))

        # draw message
        if self.msg:
            painter.setFont(QtGui.QFont("Arial", gemsedit.scaled_size(14)))
            font_metrics = painter.fontMetrics()
            ascent = font_metrics.ascent()
            descent = font_metrics.descent()
            text_width = font_metrics.horizontalAdvance(self.msg)
            padded_rect = QtCore.QRect(
                self.msg_position.x() - 6,
                self.msg_position.y() - ascent - 4,
                text_width + 12,
                ascent + descent + 8,
            )
            painter.fillRect(padded_rect, QtGui.QColor("yellow"))
            painter.setPen(QtGui.QPen(QtGui.QColor("black")))
            painter.drawText(self.msg_position, self.msg)

        # draw other objects as polygons
        if len(self.other_objects):
            line_width = 3
            font_size = QApplication.instance().font().pointSize()
            painter.setFont(QtGui.QFont("Arial", font_size))

            for param_list in self.other_objects:
                name, points_json, visible, takeable, draggable = param_list
                points = json_to_points(points_json)
                if not points:
                    continue

                # Set style based on properties
                if takeable:
                    line_color = QtGui.QColor("green")
                else:
                    line_color = QtGui.QColor("red")

                line_color.setAlpha(128)

                if visible:
                    line_type = QtCore.Qt.PenStyle.SolidLine
                else:
                    line_type = QtCore.Qt.PenStyle.DotLine

                painter.setPen(QtGui.QPen(line_color, line_width, line_type))

                # Draw polygon
                polygon = QtGui.QPolygon([QtCore.QPoint(p[0], p[1]) for p in points])
                painter.drawPolygon(polygon)

                # Draw object name at centroid
                centroid = polygon_centroid(points)
                painter.setPen(QtCore.Qt.GlobalColor.black)
                painter.setBackground(QtGui.QBrush(QtCore.Qt.GlobalColor.white))
                painter.drawText(centroid[0], centroid[1], name)

        # Draw current polygon selection
        if self.points:
            # Draw completed edges
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, 4))
            for i in range(len(self.points) - 1):
                p1, p2 = self.points[i], self.points[i + 1]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

            # Draw preview line to hover point (while drawing)
            if self.is_drawing and self.hover_point:
                # Line from last point to hover
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, 2, QtCore.Qt.PenStyle.DashLine))
                last = self.points[-1]
                painter.drawLine(last[0], last[1], self.hover_point[0], self.hover_point[1])

                # Draw dashed closing line preview (from hover to first point)
                if len(self.points) >= 2:
                    first = self.points[0]
                    painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.cyan, 2, QtCore.Qt.PenStyle.DotLine))
                    painter.drawLine(self.hover_point[0], self.hover_point[1], first[0], first[1])

            # Draw vertices as circles
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, 2))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.yellow))
            for i, p in enumerate(self.points):
                radius = 8 if i == 0 else 5  # First point larger
                painter.drawEllipse(p[0] - radius, p[1] - radius, radius * 2, radius * 2)

            # If closed polygon (not drawing), draw closing edge
            if not self.is_drawing and len(self.points) >= 3:
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, 4))
                painter.drawLine(self.points[-1][0], self.points[-1][1], self.points[0][0], self.points[0][1])

        # shutdown painter
        painter.end()

        super().paintEvent(event)

    def keyPressEvent(self, event):
        # Track shift key for constrained drawing
        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.shift_held = True
            return

        if event.key() == QtCore.Qt.Key.Key_Backspace:
            # Undo last point (same as right-click)
            if self.is_drawing and len(self.points) > 1:
                self.points.pop()
                self.update()
            elif self.is_drawing and len(self.points) == 1:
                self.points = []
                self.is_drawing = False
                self.setMouseTracking(False)
                self.msg = "Click to start drawing polygon."
                self.update()
            return

        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if len(self.points) >= 3:
                self._keep_result = True
                self._result = self.points.copy()
            self.close()
            return

        if event.key() == QtCore.Qt.Key.Key_Escape:
            # Cancel selection and close without changes
            self.points = []
            self._result = []
            self._keep_result = False
            self.close()
            return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.shift_held = False
        super().keyReleaseEvent(event)
