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

from PySide6 import QtCore, QtGui, QtSql
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

import gemsedit
from gemsedit.utils.polygon_utils import json_to_points, points_to_bounding_rect


class ViewItemWidget(QWidget):
    """Custom widget for displaying a view item with thumbnail, ID, and name."""

    def __init__(self, view_id: int, view_name: str, fg_pic_path: str, parent=None):
        super().__init__(parent)
        self.view_id = view_id
        self.view_name = view_name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(15)

        # Thumbnail label (sized to fit 200px item height with margins)
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(240, 180)
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setStyleSheet("border: 1px solid gray; background-color: #333;")

        if fg_pic_path and os.path.exists(fg_pic_path):
            pixmap = QPixmap(fg_pic_path)
            if not pixmap.isNull():
                self.thumbnail.setPixmap(pixmap)
            else:
                self.thumbnail.setText("N/A")
                self.thumbnail.setStyleSheet(
                    f"border: 1px solid gray; background-color: #333; font-size: {gemsedit.scaled_size(18)}px;"
                )
                self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)
        else:
            self.thumbnail.setText("N/A")
            self.thumbnail.setStyleSheet(
                f"border: 1px solid gray; background-color: #333; font-size: {gemsedit.scaled_size(18)}px;"
            )
            self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.thumbnail)

        # Info layout (ID and Name)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        id_label = QLabel(f"ID: {view_id}")
        id_label.setStyleSheet(f"font-weight: bold; font-size: {gemsedit.scaled_size(18)}px;")
        info_layout.addWidget(id_label)

        name_label = QLabel(view_name)
        name_label.setStyleSheet(f"font-size: {gemsedit.scaled_size(20)}px;")
        name_label.setWordWrap(True)
        info_layout.addWidget(name_label)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)


class ViewChooserDialog(QDialog):
    """Dialog for choosing a view with visual thumbnails."""

    def __init__(self, media_path: str, current_value: str = "", parent=None):
        super().__init__(parent)
        self.media_path = media_path
        self.current_value = current_value
        self.selected_value = None

        self.setWindowTitle("Choose View")
        self.setMinimumSize(650, 700)
        self.resize(700, 800)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

        self.setup_ui()
        self.load_views()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header label
        header = QLabel("Select a view:")
        header.setStyleSheet(f"font-size: {gemsedit.scaled_size(22)}px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(header)

        # List widget for views
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(f"font-size: {gemsedit.scaled_size(18)}px; padding: 8px 20px;")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.select_button = QPushButton("Select")
        self.select_button.setStyleSheet(f"font-size: {gemsedit.scaled_size(18)}px; padding: 8px 20px;")
        self.select_button.clicked.connect(self.on_select)
        self.select_button.setEnabled(False)
        self.select_button.setDefault(True)
        button_layout.addWidget(self.select_button)

        layout.addLayout(button_layout)

    def load_views(self):
        self.list_widget.clear()

        # Parse current value to find matching ID
        current_id = None
        if self.current_value and ":" in self.current_value:
            try:
                current_id = int(self.current_value.split(":")[0])
            except ValueError:
                pass

        query = QtSql.QSqlQuery()
        query.exec("SELECT Id, Name, Foreground FROM views ORDER BY RowOrder")

        select_index = -1
        index = 0

        if query.isActive():
            while query.next():
                view_id = query.value(0)
                view_name = query.value(1)
                fg_pic = query.value(2) or ""

                # Build full path for foreground image
                fg_pic_path = ""
                if fg_pic and self.media_path:
                    fg_pic_path = os.path.join(self.media_path, fg_pic)

                # Create list item
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.ItemDataRole.UserRole, f"{view_id}:{view_name}")
                item.setSizeHint(QtCore.QSize(0, 200))

                # Create custom widget
                widget = ViewItemWidget(view_id, view_name, fg_pic_path)
                self.list_widget.setItemWidget(item, widget)

                # Track if this matches current selection
                if current_id is not None and view_id == current_id:
                    select_index = index

                index += 1

        # Select the current item if found
        if select_index >= 0:
            self.list_widget.setCurrentRow(select_index)
            self.list_widget.scrollToItem(self.list_widget.item(select_index))

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        self.select_button.setEnabled(len(items) > 0)

    def on_item_double_clicked(self, item: QListWidgetItem):
        self.selected_value = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def on_select(self):
        items = self.list_widget.selectedItems()
        if items:
            self.selected_value = items[0].data(Qt.ItemDataRole.UserRole)
            self.accept()

    @staticmethod
    def choose_view(media_path: str, current_value: str = "", parent=None) -> str | None:
        """
        Static convenience method to show dialog and get result.

        Returns the selected view in "id:name" format, or None if cancelled.
        """
        dialog = ViewChooserDialog(media_path, current_value, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_value
        return None


class ObjectItemWidget(QWidget):
    """Custom widget for displaying an object item with thumbnail, IDs, and names."""

    def __init__(
        self,
        obj_id: int,
        obj_name: str,
        view_id: int,
        view_name: str,
        fg_pic_path: str,
        points_json: str,
        parent=None,
    ):
        super().__init__(parent)
        self.obj_id = obj_id
        self.obj_name = obj_name
        self.view_id = view_id
        self.view_name = view_name

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(15)

        # Thumbnail label (sized to fit 200px item height with margins)
        self.thumbnail = QLabel()
        self.thumbnail.setFixedSize(240, 180)
        self.thumbnail.setScaledContents(True)
        self.thumbnail.setStyleSheet("border: 1px solid gray; background-color: #333;")

        thumbnail_set = False
        if fg_pic_path and os.path.exists(fg_pic_path) and points_json:
            points = json_to_points(points_json)
            if points:
                left, top, width, height = points_to_bounding_rect(points)
                if width > 0 and height > 0:
                    pixmap = QPixmap(fg_pic_path)
                    if not pixmap.isNull():
                        # Create polygon-clipped thumbnail
                        cropped = self._create_polygon_crop(pixmap, points, left, top, width, height)
                        if not cropped.isNull():
                            self.thumbnail.setPixmap(cropped)
                            thumbnail_set = True

        if not thumbnail_set:
            self.thumbnail.setText("N/A")
            self.thumbnail.setStyleSheet(
                f"border: 1px solid gray; background-color: #333; font-size: {gemsedit.scaled_size(18)}px;"
            )
            self.thumbnail.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.thumbnail)

        # Info layout (Object ID/Name and View ID/Name)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)

        # Object info
        obj_id_label = QLabel(f"Object ID: {obj_id}")
        obj_id_label.setStyleSheet(f"font-weight: bold; font-size: {gemsedit.scaled_size(18)}px;")
        info_layout.addWidget(obj_id_label)

        obj_name_label = QLabel(obj_name)
        obj_name_label.setStyleSheet(f"font-size: {gemsedit.scaled_size(20)}px;")
        obj_name_label.setWordWrap(True)
        info_layout.addWidget(obj_name_label)

        # Separator/spacing
        info_layout.addSpacing(8)

        # View info (smaller, secondary)
        view_label = QLabel(f"View {view_id}: {view_name}")
        view_label.setStyleSheet(f"font-size: {gemsedit.scaled_size(14)}px; color: #666;")
        view_label.setWordWrap(True)
        info_layout.addWidget(view_label)

        info_layout.addStretch()
        layout.addLayout(info_layout, 1)

    def _create_polygon_crop(
        self, source: QPixmap, points: list, left: int, top: int, width: int, height: int
    ) -> QPixmap:
        """Create a polygon-masked crop of the source image."""
        result = QPixmap(width, height)
        result.fill(Qt.GlobalColor.transparent)

        path = QtGui.QPainterPath()
        local_points = [[p[0] - left, p[1] - top] for p in points]
        if local_points:
            path.moveTo(local_points[0][0], local_points[0][1])
            for p in local_points[1:]:
                path.lineTo(p[0], p[1])
            path.closeSubpath()

        painter = QtGui.QPainter(result)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, source, left, top, width, height)
        painter.end()

        return result


class ObjectChooserDialog(QDialog):
    """Dialog for choosing an object with visual thumbnails."""

    def __init__(self, media_path: str, current_value: str = "", parent=None):
        super().__init__(parent)
        self.media_path = media_path
        self.current_value = current_value
        self.selected_value = None

        self.setWindowTitle("Choose Object")
        self.setMinimumSize(700, 750)
        self.resize(750, 850)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

        self.setup_ui()
        self.load_objects()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Header label
        header = QLabel("Select an object:")
        header.setStyleSheet(f"font-size: {gemsedit.scaled_size(22)}px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(header)

        # List widget for objects
        self.list_widget = QListWidget()
        self.list_widget.setSpacing(2)
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.list_widget)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet(f"font-size: {gemsedit.scaled_size(18)}px; padding: 8px 20px;")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.select_button = QPushButton("Select")
        self.select_button.setStyleSheet(f"font-size: {gemsedit.scaled_size(18)}px; padding: 8px 20px;")
        self.select_button.clicked.connect(self.on_select)
        self.select_button.setEnabled(False)
        self.select_button.setDefault(True)
        button_layout.addWidget(self.select_button)

        layout.addLayout(button_layout)

    def load_objects(self):
        self.list_widget.clear()

        # Parse current value to find matching object ID
        # Format is "obj_id:view_name:obj_name"
        current_obj_id = None
        if self.current_value and ":" in self.current_value:
            try:
                current_obj_id = int(self.current_value.split(":")[0])
            except ValueError:
                pass

        # Build a lookup for view foreground images
        view_fg_pics = {}
        view_names = {}
        view_query = QtSql.QSqlQuery()
        view_query.exec("SELECT Id, Name, Foreground FROM views")
        if view_query.isActive():
            while view_query.next():
                vid = view_query.value(0)
                vname = view_query.value(1)
                vfg = view_query.value(2) or ""
                view_names[vid] = vname
                view_fg_pics[vid] = vfg

        # Query objects ordered by view then object (include Points for polygon thumbnail)
        query = QtSql.QSqlQuery()
        query.exec("SELECT Id, Parent, Name, Points FROM objects ORDER BY Parent, RowOrder")

        select_index = -1
        index = 0

        if query.isActive():
            while query.next():
                obj_id = query.value(0)
                parent_view_id = query.value(1)
                obj_name = query.value(2)
                points_json = query.value(3) or "[]"

                view_name = view_names.get(parent_view_id, "Unknown")
                fg_pic = view_fg_pics.get(parent_view_id, "")

                # Build full path for foreground image
                fg_pic_path = ""
                if fg_pic and self.media_path:
                    fg_pic_path = os.path.join(self.media_path, fg_pic)

                # Create list item - store in format expected by param_select
                item = QListWidgetItem(self.list_widget)
                item.setData(Qt.ItemDataRole.UserRole, f"{obj_id}:{view_name}:{obj_name}")
                item.setSizeHint(QtCore.QSize(0, 200))

                # Create custom widget with polygon points for cropped thumbnail
                widget = ObjectItemWidget(obj_id, obj_name, parent_view_id, view_name, fg_pic_path, points_json)
                self.list_widget.setItemWidget(item, widget)

                # Track if this matches current selection
                if current_obj_id is not None and obj_id == current_obj_id:
                    select_index = index

                index += 1

        # Select the current item if found
        if select_index >= 0:
            self.list_widget.setCurrentRow(select_index)
            self.list_widget.scrollToItem(self.list_widget.item(select_index))

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        self.select_button.setEnabled(len(items) > 0)

    def on_item_double_clicked(self, item: QListWidgetItem):
        self.selected_value = item.data(Qt.ItemDataRole.UserRole)
        self.accept()

    def on_select(self):
        items = self.list_widget.selectedItems()
        if items:
            self.selected_value = items[0].data(Qt.ItemDataRole.UserRole)
            self.accept()

    @staticmethod
    def choose_object(media_path: str, current_value: str = "", parent=None) -> str | None:
        """
        Static convenience method to show dialog and get result.

        Returns the selected object in "obj_id:view_name:obj_name" format, or None if cancelled.
        """
        dialog = ObjectChooserDialog(media_path, current_value, parent)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.selected_value
        return None
