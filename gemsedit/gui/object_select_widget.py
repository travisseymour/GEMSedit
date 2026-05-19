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

        # Zoom and pan state
        self.zoom_scale = 1.0
        self.zoom_min = 1.0
        self.zoom_max = 8.0
        self.zoom_step = 1.15  # Multiplier per scroll step
        self.pan_offset = [0, 0]  # [x, y] offset in image coordinates
        self.is_panning = False
        self.pan_start = None  # Screen position where pan started
        self.pan_start_offset = None  # Offset when pan started

        self.msg = "Press ENTER to close this window."
        self.msg_in_top_left = True  # Toggle between top-left and bottom-right
        self.msg_proximity_threshold = 80  # Pixels from message box to trigger move

        if self.allow_selection:
            self.msg = "Click to place polygon points. Click near start point to close. Scroll to zoom."
        else:
            self.msg = "Press ENTER to close."

        QtCore.QTimer.singleShot(1000, self.allow_clicks)  # Avoids ghost click from objects ui

        # Enable mouse tracking to detect when mouse is near message box
        self.setMouseTracking(True)

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

            # Don't allow panning beyond image bounds
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

        if not self.allow_selection or not self.clicks_allowed:
            return super().mousePressEvent(event)

        screen_pos = [event.pos().x(), event.pos().y()]
        img_pos = self._screen_to_image(screen_pos)

        if event.button() == QtCore.Qt.MouseButton.LeftButton:
            if not self.is_drawing:
                # Start new polygon
                self.points = [img_pos]
                self.is_drawing = True
                self.setMouseTracking(True)
                self.msg = "Click to add points. Click near start to close. Right-click to undo. Scroll to zoom."
            else:
                # Check if closing polygon (click near first point in screen coords)
                first_screen = self._image_to_screen(self.points[0])
                if len(self.points) >= 3 and is_point_near(screen_pos, first_screen, self.close_threshold):
                    self._close_polygon()
                else:
                    # Apply shift constraint if held (in image coords)
                    if self.shift_held and len(self.points) > 0:
                        img_pos = self._constrain_point(img_pos)
                    self.points.append(img_pos)
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

        if self.allow_selection and self.is_drawing:
            screen_pos = [event.pos().x(), event.pos().y()]
            img_pos = self._screen_to_image(screen_pos)
            if self.shift_held and len(self.points) > 0:
                img_pos = self._constrain_point(img_pos)
            self.hover_point = img_pos
            self.update()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        if event.button() == QtCore.Qt.MouseButton.MiddleButton:
            self.is_panning = False
            self.pan_start = None
            self.setCursor(QtCore.Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """Handle mouse wheel for zooming."""
        # Get the position under the mouse in image coordinates (before zoom)
        mouse_pos = [event.position().x(), event.position().y()]
        img_pos_before = self._screen_to_image([int(mouse_pos[0]), int(mouse_pos[1])])

        # Calculate new zoom level
        delta = event.angleDelta().y()
        if delta > 0:
            new_scale = min(self.zoom_max, self.zoom_scale * self.zoom_step)
        else:
            new_scale = max(self.zoom_min, self.zoom_scale / self.zoom_step)

        if new_scale != self.zoom_scale:
            self.zoom_scale = new_scale

            # Adjust pan so the point under the mouse stays in the same screen position
            # screen_pos = (img_pos - pan_offset) * zoom_scale
            # We want: mouse_pos = (img_pos_before - new_pan_offset) * new_scale
            # So: new_pan_offset = img_pos_before - mouse_pos / new_scale
            self.pan_offset[0] = img_pos_before[0] - mouse_pos[0] / self.zoom_scale
            self.pan_offset[1] = img_pos_before[1] - mouse_pos[1] / self.zoom_scale
            self._clamp_pan_offset()
            self.update()

        event.accept()

    def paintEvent(self, event):
        # setup painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QtGui.QPainter.RenderHint.SmoothPixmapTransform, True)

        # Apply zoom and pan transformation
        painter.scale(self.zoom_scale, self.zoom_scale)
        painter.translate(-self.pan_offset[0], -self.pan_offset[1])

        # draw image
        if self.bgPic:
            painter.drawPixmap(0, 0, QtGui.QPixmap(self.bgPic))

        # draw other objects as polygons (in image coordinates)
        if len(self.other_objects):
            line_width = max(1, int(3 / self.zoom_scale))  # Adjust line width for zoom
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

        # Draw current polygon selection (in image coordinates)
        if self.points:
            # Draw completed edges
            line_width = max(2, int(4 / self.zoom_scale))
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, line_width))
            for i in range(len(self.points) - 1):
                p1, p2 = self.points[i], self.points[i + 1]
                painter.drawLine(p1[0], p1[1], p2[0], p2[1])

            # Draw preview line to hover point (while drawing)
            if self.is_drawing and self.hover_point:
                # Line from last point to hover
                thin_width = max(1, int(2 / self.zoom_scale))
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, thin_width, QtCore.Qt.PenStyle.DashLine))
                last = self.points[-1]
                painter.drawLine(last[0], last[1], self.hover_point[0], self.hover_point[1])

                # Draw dashed closing line preview (from hover to first point)
                if len(self.points) >= 2:
                    first = self.points[0]
                    painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.cyan, thin_width, QtCore.Qt.PenStyle.DotLine))
                    painter.drawLine(self.hover_point[0], self.hover_point[1], first[0], first[1])

            # Draw vertices as circles
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, max(1, int(2 / self.zoom_scale))))
            painter.setBrush(QtGui.QBrush(QtCore.Qt.GlobalColor.yellow))
            for i, p in enumerate(self.points):
                radius = max(4, int((8 if i == 0 else 5) / self.zoom_scale))
                painter.drawEllipse(p[0] - radius, p[1] - radius, radius * 2, radius * 2)

            # If closed polygon (not drawing), draw closing edge
            if not self.is_drawing and len(self.points) >= 3:
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, line_width))
                painter.drawLine(self.points[-1][0], self.points[-1][1], self.points[0][0], self.points[0][1])

        # Reset transform for UI elements (draw in screen coordinates)
        painter.resetTransform()

        # draw message
        if self.msg:
            painter.setFont(QtGui.QFont("Arial", gemsedit.scaled_size(14)))
            font_metrics = painter.fontMetrics()
            ascent = font_metrics.ascent()
            descent = font_metrics.descent()
            text_width = font_metrics.horizontalAdvance(self.msg)

            # Calculate position based on which corner
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

        if event.key() == QtCore.Qt.Key.Key_0:
            # Reset zoom to 1:1
            self.zoom_scale = 1.0
            self.pan_offset = [0, 0]
            self.update()
            return

        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == QtCore.Qt.Key.Key_Shift:
            self.shift_held = False
        super().keyReleaseEvent(event)
