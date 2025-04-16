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

from PySide6.QtCore import Qt, QSize
from PySide6.QtCore import QDate
from PySide6.QtGui import QTextDocument, QColor
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QSpinBox,
    QDateEdit,
    QLineEdit,
    QApplication,
    QStyle,
)

from gemsedit.database import param_select
from gemsedit.gui import richtextlineedit


class GenericDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(GenericDelegate, self).__init__(parent)
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
        super(IntegerColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum

    def createEditor(self, parent, option, index):
        spinbox = QSpinBox(parent)
        spinbox.setRange(self.minimum, self.maximum)
        spinbox.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
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
                raise ValueError(
                    f"setEditorData called on IntegerColumnDelegate from invalid {value=}"
                )
        editor.setValue(value)

    def setModelData(self, editor, model, index):
        # assumes editor has 2 attributes: 'interpretText' and 'value'
        editor.interpretText()
        model.setData(index, editor.value(), Qt.ItemDataRole.EditRole)


class DateColumnDelegate(QStyledItemDelegate):

    def __init__(
        self,
        minimum=QDate(),
        maximum=QDate.currentDate(),
        format="yyyy-MM-dd",
        parent=None,
    ):
        super(DateColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.format = format

    def createEditor(self, parent, option, index):
        dateedit = QDateEdit(parent)
        dateedit.setDateRange(self.minimum, self.maximum)
        dateedit.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        )
        dateedit.setDisplayFormat(self.format)
        dateedit.setCalendarPopup(True)
        return dateedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setDate(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date())


class PlainTextColumnDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(PlainTextColumnDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        lineedit = QLineEdit(parent)
        return lineedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class ActionColumnDelegate(QStyledItemDelegate):

    def __init__(self, coltype, actiontype, mediapath, parent=None):
        super(ActionColumnDelegate, self).__init__(parent)
        self.coltype = coltype
        self.actiontype = actiontype
        self.paramselector = None
        self.mediapath = mediapath

    def createEditor(self, parent, option, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        self.paramselector = param_select.ParamSelect(
            self.coltype, value, self.actiontype, self.mediapath
        )  # 'PortalTo("EndRoom")'
        editor = self.paramselector.ParmSelectWindow
        editor.setMinimumHeight(591)
        editor.setMinimumWidth(631)
        # editor.setModal(True)
        # editor.repaint()

        return editor

    def setEditorData(self, editor, index):
        # value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        # self.paramselector.setParamString(value)
        pass

    def setModelData(self, editor, model, index):
        # print("trying to set model data: %s" % self.paramselector.result)
        if self.paramselector.result is not None:
            model.setData(index, str(self.paramselector.result))
            # print("reslting model data is: %s" % index.model().data(index, Qt.ItemDataRole.DisplayRole))


class RichTextColumnDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(RichTextColumnDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.StateFlag.State_Selected:
            document.setHtml(
                "<font color={}>{}</font>".format(
                    palette.highlightedText().color().name(), text
                )
            )
        else:
            document.setHtml(text)
        painter.save()
        color = (
            palette.highlight().color()
            if option.state & QStyle.StateFlag.State_Selected
            else QColor(index.model().data(index, Qt.ItemDataRole.BackgroundColorRole))
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
        return QSize(document.idealWidth() + 5, option.fontMetrics.height())

    def createEditor(self, parent, option, index):
        lineedit = richtextlineedit.RichTextLineEdit(parent)
        return lineedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setHtml(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.toSimpleHtml())
