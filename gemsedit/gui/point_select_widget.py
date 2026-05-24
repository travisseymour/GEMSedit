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
from PySide6.QtWidgets import QApplication

import gemsedit
from gemsedit.utils.polygon_utils import json_to_points, polygon_centroid


class PointSelect(QtWidgets.QDialog):
    """Dialog for selecting a single point on a view image.

    Shows the view's foreground image with existing objects displayed
    for reference. The user can click to select a point, with the
    current mouse position shown in the window title.
    """

    def __init__(
        self,
        parent=None,
        current_view=None,
        media_path=None,
        initial_x=0,
        initial_y=0,
    ):
        super().__init__(parent)
        self.current_view = current_view
        self.media_path = media_path
        self.clicks_allowed = False
        self.other_objects = []  # List of (name, points_json, visible, takeable, draggable)
        self.bgPic = None
        self._result_x: int = initial_x
        self._result_y: int = initial_y
        self._keep_result = False

        # Crosshair position (current mouse position in image coords)
        self.crosshair_pos: list[int] | None = None

        # Zoom and pan state
        self.zoom_scale = 1.0
        self.zoom_min = 1.0
        self.zoom_max = 8.0
        self.zoom_step = 1.15
        self.pan_offset = [0, 0]
        self.is_panning = False
        self.pan_start = None
        self.pan_start_offset = None

        self.msg = "Click to select point. Scroll to zoom. Press ENTER to confirm."
        self.msg_in_top_left = True
        self.msg_proximity_threshold = 80

        self.setWindowTitle(f"Select Point - Position: ({initial_x}, {initial_y})")

        QtCore.QTimer.singleShot(500, self.allow_clicks)

        self.setMouseTracking(True)

    def allow_clicks(self):
        self.clicks_allowed = True

    def showEvent(self, event):
        # Load the view's foreground image
        if self.current_view is not None:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM views where Id = :viewid order by RowOrder")
            query.bindValue(":viewid", self.current_view)
            query.exec()
            if query.isActive():
                query.first()
                foreground = os.path.join(self.media_path, query.value(2))
                if os.path.isfile(foreground):
                    self.bgPic = foreground

        # Load objects for this view (for reference display)
        query = QtSql.QSqlQuery()
        query.prepare(
            "SELECT Id, Name, Points, Visible, Takeable, Draggable FROM objects WHERE Parent = :viewid ORDER BY RowOrder"
        )
        query.bindValue(":viewid", self.current_view)
        query.exec()
        if query.isActive():
            while query.next():
                name = query.value(1)
                points_json = query.value(2) or "[]"
                visible = query.value(3)
                takeable = query.value(4)
                draggable = query.value(5)
                self.other_objects.append((name, points_json, visible, takeable, draggable))

        super().showEvent(event)

    def closeEvent(self, event):
        if not self._keep_result:
            self._result_x = -1
            self._result_y = -1
        super().closeEvent(event)

    def get_result(self) -> tuple[int, int]:
        """Return the selected point coordinates."""
        return (self._result_x, self._result_y)

    def _screen_to_image(self, screen_pos: list[int]) -> list[int]:
        """Convert screen coordinates to image coordinates."""
        img_x = int((screen_pos[0] / self.zoom_scale) + self.pan_offset[0])
        img_y = int((screen_pos[1] / self.zoom_scale) + self.pan_offset[1])
        return [img_x, img_y]

    def _image_to_screen(self, img_pos: list[int]) -> list[int]:
        """Convert image coordinates to screen coordinates."""
        screen_x = int((img_pos[0] - self.pan_offset[0]) * self.zoom_scale)
        screen_y = int((img_pos[1] - self.pan_offset[1]) * self.zoom_scale)
        return [screen_x, screen_y]

    def _clamp_pan_offset(self):
        """Ensure pan offset doesn't go out of bounds."""
        if self.bgPic:
            pixmap = QtGui.QPixmap(self.bgPic)
            img_w, img_h = pixmap.width(), pixmap.height()
            view_w, view_h = self.width() / self.zoom_scale, self.height() / self.zoom_scale

            max_x = max(0, img_w - view_w)
            max_y = max(0, img_h - view_h)
            self.pan_offset[0] = max(0, min(self.pan_offset[0], max_x))
            self.pan_offset[1] = max(0, min(self.pan_offset[1], max_y))

    def _get_msg_rect(self) -> QtCore.QRect:
        """Get the current message box rectangle in screen coordinates."""
        if not self.msg:
            return QtCore.QRect()

        font = QtGui.QFont("Arial", gemsedit.scaled_size(14))
        font_metrics = QtGui.QFontMetrics(font)
        ascent = font_metrics.ascent()
        descent = font_metrics.descent()
        text_width = font_metrics.horizontalAdvance(self.msg)

        if self.msg_in_top_left:
            msg_x = 20
            msg_y = 20
        else:
            msg_x = self.width() - text_width - 20
            msg_y = self.height() - descent - 20

        return QtCore.QRect(
            msg_x - 6,
            msg_y - ascent - 4,
            text_width + 12,
            ascent + descent + 8,
        )

    def mousePressEvent(self, event):
        # Handle middle button for panning
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = True
            self.pan_start = [event.pos().x(), event.pos().y()]
            self.pan_start_offset = self.pan_offset.copy()
            self.setCursor(QtCore.Qt.CursorShape.ClosedHandCursor)
            return

        if not self.clicks_allowed:
            return super().mousePressEvent(event)

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            screen_pos = [event.pos().x(), event.pos().y()]
            img_pos = self._screen_to_image(screen_pos)
            self._result_x = img_pos[0]
            self._result_y = img_pos[1]
            self._keep_result = True
            self.setWindowTitle(f"Select Point - Position: ({self._result_x}, {self._result_y}) - SELECTED")
            self.msg = f"Point selected at ({self._result_x}, {self._result_y}). Press ENTER to confirm, ESC to cancel."
            self.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # Handle panning
        if self.is_panning and self.pan_start is not None:
            dx = (event.pos().x() - self.pan_start[0]) / self.zoom_scale
            dy = (event.pos().y() - self.pan_start[1]) / self.zoom_scale
            self.pan_offset[0] = self.pan_start_offset[0] - dx
            self.pan_offset[1] = self.pan_start_offset[1] - dy
            self._clamp_pan_offset()
            self.update()
            return

        # Update crosshair position
        screen_pos = [event.pos().x(), event.pos().y()]
        self.crosshair_pos = self._screen_to_image(screen_pos)

        # Update window title with current position
        if self.crosshair_pos:
            self.setWindowTitle(f"Select Point - Position: ({self.crosshair_pos[0]}, {self.crosshair_pos[1]})")

        # Check if mouse is near message box and move it out of the way
        if self.msg:
            msg_rect = self._get_msg_rect()
            expanded_rect = msg_rect.adjusted(
                -self.msg_proximity_threshold,
                -self.msg_proximity_threshold,
                self.msg_proximity_threshold,
                self.msg_proximity_threshold,
            )
            if expanded_rect.contains(event.pos()):
                self.msg_in_top_left = not self.msg_in_top_left

        self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.pan_start = None
            self.setCursor(QtCore.Qt.CursorShape.CrossCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Handle mouse wheel for zooming."""
        mouse_pos = [event.position().x(), event.position().y()]
        img_pos_before = self._screen_to_image([int(mouse_pos[0]), int(mouse_pos[1])])

        delta = event.angleDelta().y()
        if delta > 0:
            new_scale = min(self.zoom_max, self.zoom_scale * self.zoom_step)
        else:
            new_scale = max(self.zoom_min, self.zoom_scale / self.zoom_step)

        if new_scale != self.zoom_scale:
            self.zoom_scale = new_scale
            self.pan_offset[0] = img_pos_before[0] - mouse_pos[0] / self.zoom_scale
            self.pan_offset[1] = img_pos_before[1] - mouse_pos[1] / self.zoom_scale
            self._clamp_pan_offset()
            self.update()

        event.accept()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)

        # Apply zoom and pan transformation
        painter.scale(self.zoom_scale, self.zoom_scale)
        painter.translate(-self.pan_offset[0], -self.pan_offset[1])

        # Draw background image
        if self.bgPic:
            painter.drawPixmap(0, 0, QtGui.QPixmap(self.bgPic))

        # Draw other objects as polygons for reference
        if len(self.other_objects):
            line_width = max(1, int(3 / self.zoom_scale))
            font_size = max(8, int(QApplication.instance().font().pointSize() / self.zoom_scale))
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

        # Draw crosshair at current mouse position
        if self.crosshair_pos:
            crosshair_size = max(10, int(20 / self.zoom_scale))
            line_width = max(1, int(2 / self.zoom_scale))
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.cyan, line_width))
            cx, cy = self.crosshair_pos
            painter.drawLine(cx - crosshair_size, cy, cx + crosshair_size, cy)
            painter.drawLine(cx, cy - crosshair_size, cx, cy + crosshair_size)

        # Draw selected point marker if we have a selection
        if self._keep_result:
            marker_size = max(8, int(15 / self.zoom_scale))
            line_width = max(2, int(3 / self.zoom_scale))
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, line_width))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.yellow))
            painter.drawEllipse(
                self._result_x - marker_size // 2,
                self._result_y - marker_size // 2,
                marker_size,
                marker_size,
            )

        # Reset transform for UI elements
        painter.resetTransform()

        # Draw message
        if self.msg:
            painter.setFont(QtGui.QFont("Arial", gemsedit.scaled_size(14)))
            font_metrics = painter.fontMetrics()
            ascent = font_metrics.ascent()
            descent = font_metrics.descent()
            text_width = font_metrics.horizontalAdvance(self.msg)

            if self.msg_in_top_left:
                msg_x = 20
                msg_y = 20
            else:
                msg_x = self.width() - text_width - 20
                msg_y = self.height() - descent - 20

            padded_rect = QtCore.QRect(
                msg_x - 6,
                msg_y - ascent - 4,
                text_width + 12,
                ascent + descent + 8,
            )
            painter.fillRect(padded_rect, QtGui.QColor("yellow"))
            painter.setPen(QtGui.QPen(QtGui.QColor("black")))
            painter.drawText(msg_x, msg_y, self.msg)

        # Draw zoom indicator if zoomed
        if self.zoom_scale != 1.0:
            zoom_text = f"Zoom: {self.zoom_scale:.1f}x (Middle-drag to pan)"
            painter.setFont(QtGui.QFont("Arial", gemsedit.scaled_size(12)))
            font_metrics = painter.fontMetrics()
            text_width = font_metrics.horizontalAdvance(zoom_text)
            x_pos = self.width() - text_width - 20
            y_pos = 30
            padded_rect = QtCore.QRect(
                x_pos - 6,
                y_pos - font_metrics.ascent() - 4,
                text_width + 12,
                font_metrics.ascent() + font_metrics.descent() + 8,
            )
            painter.fillRect(padded_rect, QtGui.QColor(0, 0, 0, 180))
            painter.setPen(QtGui.QPen(QtGui.QColor("white")))
            painter.drawText(x_pos, y_pos, zoom_text)

        painter.end()
        super().paintEvent(event)

    def keyPressEvent(self, event):
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            if self._keep_result:
                self.accept()
            return

        if event.key() == QtCore.Qt.Key.Key_Escape:
            self._keep_result = False
            self.reject()
            return

        if event.key() == QtCore.Qt.Key.Key_0:
            # Reset zoom to 1:1
            self.zoom_scale = 1.0
            self.pan_offset = [0, 0]
            self.update()
            return

        super().keyPressEvent(event)
