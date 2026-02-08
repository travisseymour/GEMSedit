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

from PySide6.QtCore import QDate, QSize, Qt
from PySide6.QtGui import QColor, QTextDocument
from PySide6.QtWidgets import (
    QApplication,
    QDateEdit,
    QLineEdit,
    QSpinBox,
    QStyle,
    QStyledItemDelegate,
)

from gemsedit.database import param_select
from gemsedit.gui import richtextlineedit


class GenericDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.delegates = {}

    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)
        self.delegates[column] = delegate

    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]

    def paint(self, painter, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)

    def createEditor(self, parent, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QStyledItemDelegate.createEditor(self, parent, option, index)

    def setEditorData(self, editor, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)

    def setModelData(self, editor, model, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


class IntegerColumnDelegate(QStyledItemDelegate):
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
        # aasumes editor has attribute 'setValue'
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        match value:
            case "True":
                value = 1
            case "False":
                value = 0
            case _:
                raise ValueError(f"setEditorData called on IntegerColumnDelegate from invalid {value=}")
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        # assumes editor has 2 attributes: 'interpretText' and 'value'
        editor.interpretText()
        model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)


class DateColumnDelegate(QStyledItemDelegate):
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


class PlainTextColumnDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def createEditor(self, parent, option, index):
        line_edit = QLineEdit(parent)
        return line_edit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class ActionColumnDelegate(QStyledItemDelegate):
    def __init__(self, col_type, action_type, media_path, parent=None):
        super().__init__(parent)
        self.coltype = col_type
        self.action_type = action_type
        self.param_selector = None
        self.media_path = media_path
        self._dialog_result = None

    def createEditor(self, parent, option, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        self.param_selector = param_select.ParamSelect(
            self.coltype, value, self.action_type, self.media_path
        )

        # Create a hidden line edit as the actual delegate editor
        editor = QLineEdit(parent)
        editor.setVisible(False)

        # Show the ParamSelect dialog modally using exec()
        dialog = self.param_selector.ParmSelectWindow
        dialog.setMinimumHeight(591)
        dialog.setMinimumWidth(631)
        dialog.exec()

        # Store the result for use in setModelData
        self._dialog_result = self.param_selector.result

        return editor

    def setEditorData(self, editor, index):
        # No-op: the dialog handles all editing
        pass

    def setModelData(self, editor, model, index):
        # Use the stored dialog result directly
        if self._dialog_result is not None:
            model.setData(index, str(self._dialog_result))


class RichTextColumnDelegate(QStyledItemDelegate):
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
