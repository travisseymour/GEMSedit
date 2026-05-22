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

from PySide6 import QtCore, QtGui, QtSql
from PySide6.QtCore import Qt

from gemsedit.utils.colorlist import ultra_spaced_colors


class TaggedSqlModel(QtSql.QSqlQueryModel):
    """QSqlQueryModel subclass that colors rows based on their Tag column value."""

    def __init__(self, tag_column_index: int, parent=None):
        super().__init__(parent)
        self._tag_column_index = tag_column_index
        self._tag_color_map: dict[str, QtGui.QColor] = {}

    def set_tag_color_map(self, color_map: dict[str, QtGui.QColor]):
        self._tag_color_map = color_map
        if self.rowCount() > 0:
            top_left = self.index(0, 0)
            bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
            self.dataChanged.emit(top_left, bottom_right)

    def data(self, index: QtCore.QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.BackgroundRole:
            tag_index = self.index(index.row(), self._tag_column_index)
            tag_value = super().data(tag_index, Qt.ItemDataRole.DisplayRole)
            if tag_value and str(tag_value).strip():
                color = self._tag_color_map.get(str(tag_value).strip())
                if color is not None:
                    return color
            return None
        return super().data(index, role)


def build_tag_color_map() -> dict[str, QtGui.QColor]:
    """Query all unique non-empty tags from views and objects,
    assign each a color from ultra_spaced_colors."""
    tags: set[str] = set()
    query = QtSql.QSqlQuery()

    query.exec("SELECT DISTINCT Tag FROM views WHERE Tag IS NOT NULL AND Tag != ''")
    while query.next():
        tags.add(str(query.value(0)).strip())

    query.exec("SELECT DISTINCT Tag FROM objects WHERE Tag IS NOT NULL AND Tag != ''")
    while query.next():
        tags.add(str(query.value(0)).strip())

    sorted_tags = sorted(tags)
    color_values = list(ultra_spaced_colors.values())

    color_map: dict[str, QtGui.QColor] = {}
    for i, tag in enumerate(sorted_tags):
        hex_color = color_values[i % len(color_values)]
        color_map[tag] = QtGui.QColor(hex_color)

    return color_map
