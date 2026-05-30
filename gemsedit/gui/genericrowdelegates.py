#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import os  # only needed for fileio delegates
import re

from PySide6.QtCore import QDate, QSize, Qt
from PySide6.QtGui import QColor, QIcon, QPixmap, QTextDocument
from PySide6.QtSql import QSqlQuery
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDateEdit,
    QDoubleSpinBox,
    QFileDialog,
    QLineEdit,
    QListWidget,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
)

from gemsedit.gui import richtextlineedit
from gemsedit.gui.view_chooser import ObjectChooserDialog, ViewChooserDialog


class GenericRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.delegates = {}

    def insertRowDelegate(self, row, delegate):
        delegate.setParent(self)
        self.delegates[row] = delegate

    def removeRowDelegate(self, row):
        if row in self.delegates:
            del self.delegates[row]

    def paint(self, painter, option, index):
        delegate = self.delegates.get(index.row())
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        delegate = self.delegates.get(index.row())
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        delegate = self.delegates.get(index.row())
        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        delegate = self.delegates.get(index.row())
        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


class IntegerRowDelegate(QStyledItemDelegate):
    def __init__(self, minimum=0, maximum=100, parent=None):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum

    def createEditor(self, parent, option, index):
        spinbox = QSpinBox(parent)
        spinbox.setRange(self.minimum, self.maximum)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return spinbox

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        if value == "True":
            value = 1
        elif value == "False":
            value = 0
        else:
            value = int(value)
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, editor.value())


class FloatRowDelegate(QStyledItemDelegate):
    def __init__(self, minimum=0.0, maximum=1.0, parent=None):
        super().__init__(parent)
        self.minimum = minimum
        self.maximum = maximum

    def createEditor(self, parent, option, index):
        # spinbox = QSpinBox(parent)
        spinbox = QDoubleSpinBox(parent)
        spinbox.setRange(self.minimum, self.maximum)
        spinbox.setSingleStep(0.05)
        spinbox.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        return spinbox

    def setEditorData(self, editor, index):
        value = float(index.model().data(index, Qt.ItemDataRole.DisplayRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, float(editor.value()))


class ListRowDelegate(QStyledItemDelegate):
    def __init__(self, listitems=None, parent=None):
        super().__init__(parent)
        self.listitems = listitems

    def createEditor(self, parent, option, index):
        listwidget = QListWidget(parent)
        listwidget.addItems(self.listitems)
        return listwidget

    # *** Untested! May need to bring setEditorData and setModelData from ComboRowDelegate() [which does work]
    def setEditorData(self, editor, index):
        value = str(index.model().data(index, Qt.ItemDataRole.DisplayRole))
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.value())


class ComboRowDelegate(QStyledItemDelegate):
    def __init__(self, listitems=None, parent=None):
        super().__init__(parent)
        self.listitems = listitems

    def createEditor(self, parent, option, index):
        combowidget = QComboBox(parent)
        combowidget.addItems(self.listitems)
        return combowidget

    def setEditorData(self, editor, index):
        value = str(index.model().data(index, Qt.ItemDataRole.DisplayRole))
        editor.setEditText(value)
        editor.setCurrentIndex(editor.findText(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemText(editor.currentIndex()))


class ComboRowColoredDelegate(QStyledItemDelegate):
    def __init__(self, listitems=None, parent=None):
        super().__init__(parent)
        self.listitems = listitems  # list of these: "[NAME,R,G,B,A]"

    def createEditor(self, parent, option, index):
        combowidget = QComboBox(parent)
        # combowidget.addItems(self.listitems)
        for item in self.listitems:
            icon = QIcon()
            pixmap = QPixmap(24, 24)
            n, r, g, b, a = eval(item)
            pixmap.fill(QColor(r, g, b))
            icon.addPixmap(pixmap)
            combowidget.addItem(icon, item)
        return combowidget

    def setEditorData(self, editor, index):
        value = str(index.model().data(index, Qt.ItemDataRole.DisplayRole))
        editor.setEditText(value)
        editor.setCurrentIndex(editor.findText(value))

    def setModelData(self, editor, model, index):
        model.setData(index, editor.itemText(editor.currentIndex()))


class DirectoryRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected_dir = None

    def createEditor(self, parent, option, index):
        # Use the static getExistingDirectory method for reliable cross-platform behavior
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""

        # Determine starting directory
        if current_val and os.path.isdir(current_val):
            start_path = current_val
        elif current_val and os.path.isdir(os.path.dirname(current_val)):
            start_path = os.path.dirname(current_val)
        else:
            start_path = os.path.expanduser("~")

        directory = QFileDialog.getExistingDirectory(
            parent,
            "Choose A Directory",
            start_path,
            QFileDialog.Option.ShowDirsOnly,
        )

        if directory:
            self._selected_dir = directory
        else:
            self._selected_dir = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_dir is not None:
            editor.setText(self._selected_dir)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_dir is not None:
            model.setData(index, self._selected_dir)
        self._selected_dir = None  # Reset for next use


class FileRowDelegate(QStyledItemDelegate):
    def __init__(self, mediapath, filterstr="All Files (*.*)", parent=None):
        super().__init__(parent)
        self.filterstr = filterstr
        self.mediapath = mediapath
        self._selected_file = None

    def createEditor(self, parent, option, index):
        # Use the static getOpenFileName method for reliable cross-platform behavior
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""

        # Determine starting directory
        if current_val and os.path.exists(os.path.join(self.mediapath, current_val)):
            start_path = os.path.join(self.mediapath, current_val)
        else:
            start_path = self.mediapath

        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Choose an existing " + self.filterstr,
            start_path,
            self.filterstr,
        )

        if filename:
            self._selected_file = os.path.basename(filename)
        else:
            self._selected_file = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_file is not None:
            editor.setText(self._selected_file)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_file is not None:
            model.setData(index, self._selected_file)
        self._selected_file = None  # Reset for next use


class ExeFileRowDelegate(QStyledItemDelegate):
    """File delegate that stores the full path (for executables/applications)."""

    def __init__(self, filterstr="All Files (*.*)", parent=None):
        super().__init__(parent)
        self.filterstr = filterstr
        self._selected_file = None

    def createEditor(self, parent, option, index):
        # Use the static getOpenFileName method for reliable cross-platform behavior
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""

        # Determine starting directory from current value or use home
        if current_val and os.path.exists(current_val):
            start_path = current_val
        elif current_val and os.path.exists(os.path.dirname(current_val)):
            start_path = os.path.dirname(current_val)
        else:
            start_path = os.path.expanduser("~")

        filename, _ = QFileDialog.getOpenFileName(
            parent,
            "Choose an Application or Executable",
            start_path,
            self.filterstr,
        )

        if filename:
            self._selected_file = filename  # Store full path for executables
        else:
            self._selected_file = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_file is not None:
            editor.setText(self._selected_file)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_file is not None:
            model.setData(index, self._selected_file)
        self._selected_file = None  # Reset for next use


class DateRowDelegate(QStyledItemDelegate):
    def __init__(
        self,
        minimum: QDate | None,
        maximum: QDate | None,
        format="yyyy-MM-dd",
        parent=None,
    ):
        super().__init__(parent)
        self.minimum = QDate() if minimum is None else minimum
        self.maximum = QDate.currentDate() if maximum is None else maximum
        self.format = format

    def createEditor(self, parent, option, index):
        date_edit = QDateEdit(parent)
        date_edit.setDateRange(self.minimum, self.maximum)
        date_edit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        date_edit.setDisplayFormat(self.format)
        date_edit.setCalendarPopup(True)
        return date_edit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setDate(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date())


class PlainTextRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        line_edit = QLineEdit(parent)
        return line_edit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text().replace("(", "[").replace(")", "]"))


class RichTextRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.StateFlag.State_Selected:
            document.setHtml(f"<font color={palette.highlightedText().color().name()}>{text}</font>")
        else:
            document.setHtml(text)
        painter.save()
        color = (
            palette.highlight().color()
            if option.state & QStyle.StateFlag.State_Selected
            else QColor(index.model().data(index, Qt.ItemDataRole.BackgroundRole))
        )
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()

    def sizeHint(self, option, index):
        text = index.model().data(index)
        document = QTextDocument()
        document.setDefaultFont(option.font)
        document.setHtml(text)
        return QSize(int(document.idealWidth()) + 5, option.fontMetrics.height())

    def createEditor(self, parent, option, index):
        line_edit = richtextlineedit.RichTextLineEdit(parent)
        return line_edit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setHtml(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toSimpleHtml())


class ViewRowDelegate(QStyledItemDelegate):
    """Delegate that opens a ViewChooserDialog for selecting views with thumbnails."""

    def __init__(self, media_path: str, parent=None):
        super().__init__(parent)
        self.media_path = media_path
        self._selected_view = None

    def createEditor(self, parent, option, index):
        # Get current value
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""

        # Show the view chooser dialog
        result = ViewChooserDialog.choose_view(self.media_path, current_val, parent)

        if result:
            self._selected_view = result
        else:
            self._selected_view = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_view is not None:
            editor.setText(self._selected_view)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_view is not None:
            model.setData(index, self._selected_view)
        self._selected_view = None  # Reset for next use


class ObjectRowDelegate(QStyledItemDelegate):
    """Delegate that opens an ObjectChooserDialog for selecting objects with thumbnails."""

    def __init__(self, media_path: str, filter_view: int | None = None, parent=None):
        super().__init__(parent)
        self.media_path = media_path
        self.filter_view = filter_view
        self._selected_object = None

    def createEditor(self, parent, option, index):
        # Get current value
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""

        # Show the object chooser dialog (optionally filtered by view)
        result = ObjectChooserDialog.choose_object(self.media_path, current_val, parent, filter_view=self.filter_view)

        if result:
            self._selected_object = result
        else:
            self._selected_object = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_object is not None:
            editor.setText(self._selected_object)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_object is not None:
            model.setData(index, self._selected_object)
        self._selected_object = None  # Reset for next use


class VariableNameRowDelegate(QStyledItemDelegate):
    """Delegate with an editable combobox showing existing variable names from the environment."""

    # Patterns to extract variable names from actions/conditions
    # SetVariable("varname","value"), InputDialog("prompt","varname"), VarIncrease("varname"), etc.
    VARNAME_PATTERNS = [
        (r'SetVariable\("([^"]+)"', 1),  # First arg is varname
        (r'InputDialog\("[^"]*","([^"]+)"', 1),  # Second arg is varname
        (r'VarIncrease\("([^"]+)"', 1),  # First arg is varname
        (r'VarDecrease\("([^"]+)"', 1),  # First arg is varname
        (r'DelVariable\("([^"]+)"', 1),  # First arg is varname
        (r'VarValueIs\("([^"]+)"', 1),  # First arg is varname (condition)
        (r'VarValueIsNot\("([^"]+)"', 1),  # First arg is varname (condition)
        (r'VarExists\("([^"]+)"', 1),  # First arg is varname (condition)
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

    def _get_existing_varnames(self) -> list[str]:
        """Query the database for all variable names used in actions and conditions."""
        varnames = set()

        query = QSqlQuery()
        # Get all Action and Condition strings from the actions table
        query.exec("SELECT Action, Condition FROM actions")

        while query.next():
            action_str = query.value(0) or ""
            condition_str = query.value(1) or ""

            for text in (action_str, condition_str):
                for pattern, _group in self.VARNAME_PATTERNS:
                    match = re.search(pattern, text)
                    if match:
                        varnames.add(match.group(1))

        # Return sorted list of unique variable names
        return sorted(varnames, key=str.lower)

    def createEditor(self, parent, option, index):
        combo = QComboBox(parent)
        combo.setEditable(True)  # Allow typing new variable names

        # Populate with existing variable names
        existing_names = self._get_existing_varnames()
        combo.addItems(existing_names)

        # Set placeholder text to guide the user
        combo.lineEdit().setPlaceholderText("Select or type variable name")

        return combo

    def setEditorData(self, editor, index):
        value = str(index.model().data(index, Qt.ItemDataRole.DisplayRole) or "")
        editor.setCurrentText(value)

    def setModelData(self, editor, model, index):
        # Get the text from the combo (either selected or typed)
        value = editor.currentText().strip()
        model.setData(index, value)


class PositionRowDelegate(QStyledItemDelegate):
    """Delegate that opens a PointSelect dialog for selecting Left/Top position.

    When a point is selected, both the Left and Top values are updated together.
    """

    def __init__(
        self,
        media_path: str,
        current_view: int | None,
        param_dict: dict,
        param_key: str,
        left_row: int,
        top_row: int,
        signal_update,
        parent=None,
    ):
        super().__init__(parent)
        self.media_path = media_path
        self.current_view = current_view
        self.param_dict = param_dict
        self.param_key = param_key
        self.left_row = left_row
        self.top_row = top_row
        self.signal_update = signal_update
        self._selected_value = None

    def createEditor(self, parent, option, index):
        from gemsedit.gui.point_select_widget import PointSelect

        # Get current Left and Top values
        try:
            left_val = int(self.param_dict[self.param_key][self.left_row][2])
        except (ValueError, TypeError):
            left_val = 0
        try:
            top_val = int(self.param_dict[self.param_key][self.top_row][2])
        except (ValueError, TypeError):
            top_val = 0

        # Show the point selection dialog
        dialog = PointSelect(
            parent=parent,
            current_view=self.current_view,
            media_path=self.media_path,
            initial_x=left_val,
            initial_y=top_val,
        )
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.showMaximized()

        if dialog.exec() == dialog.DialogCode.Accepted:
            x, y = dialog.get_result()
            if x >= 0 and y >= 0:
                # Update both Left and Top values in the param_dict
                self.param_dict[self.param_key][self.left_row][2] = x
                self.param_dict[self.param_key][self.top_row][2] = y

                # Determine which value this row should return
                if index.row() == self.left_row:
                    self._selected_value = x
                else:
                    self._selected_value = y

                # Signal that values have changed
                if self.signal_update:
                    self.signal_update()
            else:
                # Keep existing value
                self._selected_value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        else:
            # Cancelled - keep existing value
            self._selected_value = index.model().data(index, Qt.ItemDataRole.DisplayRole)

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_value is not None:
            editor.setText(str(self._selected_value))
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or "0"
            editor.setText(str(val))

    def setModelData(self, editor, model, index):
        if self._selected_value is not None:
            model.setData(index, self._selected_value)
        self._selected_value = None  # Reset for next use


class ColorAlphaDialog(QStyledItemDelegate):
    """Dialog for selecting a color with alpha value."""

    def __init__(self, color_list: list[str], current_value: str, parent=None):
        from PySide6.QtWidgets import (
            QDialog,
            QDialogButtonBox,
            QHBoxLayout,
            QLabel,
            QSlider,
            QVBoxLayout,
        )

        self.dialog = QDialog(parent)
        self.dialog.setWindowTitle("Select Color")
        self.dialog.setMinimumWidth(400)

        self.color_list = color_list
        self._result = None

        # Parse current value to get initial color and alpha
        self._parse_current_value(current_value)

        layout = QVBoxLayout(self.dialog)

        # Top row: color swatch and dropdown
        top_layout = QHBoxLayout()

        # Color swatch (preview)
        self.swatch = QLabel()
        self.swatch.setFixedSize(60, 60)
        self.swatch.setStyleSheet("border: 1px solid black;")
        top_layout.addWidget(self.swatch)

        # Color dropdown
        color_layout = QVBoxLayout()
        color_label = QLabel("Color:")
        self.color_combo = QComboBox()
        for item in self.color_list:
            icon = QIcon()
            pixmap = QPixmap(24, 24)
            n, r, g, b, a = eval(item)
            pixmap.fill(QColor(r, g, b))
            icon.addPixmap(pixmap)
            # Display just the color name in the dropdown
            self.color_combo.addItem(icon, n, item)

        # Set initial selection
        for i in range(self.color_combo.count()):
            if self.color_combo.itemText(i) == self._current_name:
                self.color_combo.setCurrentIndex(i)
                break

        self.color_combo.currentIndexChanged.connect(self._update_preview)
        color_layout.addWidget(color_label)
        color_layout.addWidget(self.color_combo)
        top_layout.addLayout(color_layout)

        layout.addLayout(top_layout)

        # Alpha slider row
        alpha_layout = QHBoxLayout()
        alpha_label = QLabel("Alpha:")
        alpha_label.setFixedWidth(50)
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(self._current_alpha)
        self.alpha_slider.valueChanged.connect(self._update_preview)

        self.alpha_value_label = QLabel(str(self._current_alpha))
        self.alpha_value_label.setFixedWidth(30)

        alpha_layout.addWidget(alpha_label)
        alpha_layout.addWidget(self.alpha_slider)
        alpha_layout.addWidget(self.alpha_value_label)

        layout.addLayout(alpha_layout)

        # Output preview
        output_layout = QHBoxLayout()
        output_label = QLabel("Output:")
        self.output_preview = QLabel()
        output_layout.addWidget(output_label)
        output_layout.addWidget(self.output_preview)
        output_layout.addStretch()
        layout.addLayout(output_layout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.dialog.reject)
        layout.addWidget(buttons)

        self._update_preview()

    def _parse_current_value(self, value: str):
        """Parse a color string like ['Dark Slate Gray',47,79,79,128]"""
        self._current_name = "Black"
        self._current_r = 0
        self._current_g = 0
        self._current_b = 0
        self._current_alpha = 128  # Default alpha for shading

        try:
            parsed = eval(value)
            if isinstance(parsed, list) and len(parsed) >= 5:
                self._current_name = str(parsed[0])
                self._current_r = int(parsed[1])
                self._current_g = int(parsed[2])
                self._current_b = int(parsed[3])
                self._current_alpha = int(parsed[4])
        except Exception:
            pass

    def _update_preview(self):
        """Update the color swatch and output string based on current selections."""
        # Get selected color data
        idx = self.color_combo.currentIndex()
        color_data = self.color_combo.itemData(idx)
        if color_data:
            n, r, g, b, _ = eval(color_data)
        else:
            n, r, g, b = self._current_name, self._current_r, self._current_g, self._current_b

        alpha = self.alpha_slider.value()
        self.alpha_value_label.setText(str(alpha))

        # Update swatch with alpha
        color = QColor(r, g, b, alpha)
        # Create a checkerboard background to show transparency
        pixmap = QPixmap(60, 60)
        pixmap.fill(Qt.GlobalColor.white)
        from PySide6.QtGui import QPainter

        painter = QPainter(pixmap)
        # Draw checkerboard pattern
        for row in range(6):
            for col in range(6):
                if (row + col) % 2 == 0:
                    painter.fillRect(col * 10, row * 10, 10, 10, QColor(200, 200, 200))
        # Draw the color with alpha on top
        painter.fillRect(0, 0, 60, 60, color)
        painter.end()
        self.swatch.setPixmap(pixmap)

        # Update output preview
        output = f"['{n}',{r},{g},{b},{alpha}]"
        self.output_preview.setText(output)
        self._result = output

    def _accept(self):
        self._update_preview()  # Ensure result is current
        self.dialog.accept()

    def exec(self):
        return self.dialog.exec()

    def get_result(self) -> str | None:
        return self._result


class ColorWithAlphaRowDelegate(QStyledItemDelegate):
    """Delegate that opens a color selection dialog with alpha slider."""

    def __init__(self, color_list: list[str], parent=None):
        super().__init__(parent)
        self.color_list = color_list
        self._selected_color = None

    def createEditor(self, parent, option, index):
        from PySide6.QtWidgets import QDialog

        # Get current value
        current_val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or "['Black',0,0,0,128]"

        # Show the color selection dialog
        dialog = ColorAlphaDialog(self.color_list, current_val, parent)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._selected_color = dialog.get_result()
        else:
            self._selected_color = current_val  # Keep existing value if cancelled

        # Return a simple line edit that will immediately be populated and closed
        editor = QLineEdit(parent)
        editor.setReadOnly(True)
        return editor

    def setEditorData(self, editor, index):
        if self._selected_color is not None:
            editor.setText(self._selected_color)
        else:
            val = index.model().data(index, Qt.ItemDataRole.DisplayRole) or ""
            editor.setText(val)

    def setModelData(self, editor, model, index):
        if self._selected_color is not None:
            model.setData(index, self._selected_color)
        self._selected_color = None  # Reset for next use
