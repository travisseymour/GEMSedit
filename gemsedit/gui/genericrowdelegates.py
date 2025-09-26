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

from PySide6.QtCore import Qt, QDate, QSize
from PySide6.QtGui import QIcon, QPixmap, QColor, QTextDocument
from PySide6.QtWidgets import (
    QStyledItemDelegate,
    QSpinBox,
    QDoubleSpinBox,
    QListWidget,
    QComboBox,
    QFileDialog,
    QDialog,
    QDateEdit,
    QLineEdit,
    QApplication,
    QStyle,
)

import os  # only needed for fileio delegates

from gemsedit.gui import richtextlineedit


class GenericRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(GenericRowDelegate, self).__init__(parent)
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
        super(IntegerRowDelegate, self).__init__(parent)
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
        super(FloatRowDelegate, self).__init__(parent)
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
        super(ListRowDelegate, self).__init__(parent)
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
        super(ComboRowDelegate, self).__init__(parent)
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
        super(ComboRowColoredDelegate, self).__init__(parent)
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
    def createEditor(self, parent, option, index):
        editor = QFileDialog(parent)
        editor.filesSelected.connect(lambda: editor.setResult(QDialog.DialogCode.Accepted))
        editor.setFileMode(QFileDialog.FileMode.Directory)
        editor.setWindowTitle("Choose A Directory")
        # r = option.rect
        # r.setHeight(600)
        # r.setWidth(600)
        # editor.setGeometry(r)
        return editor

    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        fs = val.rsplit(os.path.sep, 1)
        if len(fs) == 2:
            bdir, vdir = fs
        else:
            bdir = "."
            vdir = fs[0]

        editor.setDirectory(bdir)
        editor.selectFile(vdir)

    def setModelData(self, editor, model, index):
        # model.setData(index, str(editor.selectedFiles()[0]))
        if editor.result() == QDialog.DialogCode.Accepted:
            model.setData(index, str(editor.selectedFiles()[0]))


class FileRowDelegate(QStyledItemDelegate):
    def __init__(self, mediapath, filterstr="All Files (*.*)", parent=None):
        super(FileRowDelegate, self).__init__(parent)
        self.filterstr = filterstr
        self.mediapath = mediapath
        self.oldwd = "./"

    def createEditor(self, parent, option, index):
        editor = QFileDialog(parent)
        editor.setModal(False)
        editor.setDirectory(self.mediapath)
        editor.setFileMode(QFileDialog.FileMode.ExistingFile)
        editor.setNameFilter(self.filterstr)
        editor.setWindowTitle("Choose an existing " + self.filterstr)

        editor.filesSelected.connect(lambda: editor.setResult(QDialog.DialogCode.Accepted))

        self.oldwd = os.getcwd()
        os.chdir(self.mediapath)

        return editor

    def setEditorData(self, editor, index):
        val = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        fs = val.rsplit(os.path.sep, 1)
        if len(fs) == 2:
            bdir, vdir = fs
        else:
            bdir = "."
            vdir = fs[0]

        editor.setDirectory(bdir)
        editor.selectFile(vdir)

    def setModelData(self, editor, model, index):
        # model.setData(index, str(editor.selectedFiles()[0]))
        # print("filerowdelegate: editor.result={} qdialog.accepted={}".format(editor.result(),QDialog.Accepted))
        if editor.result() == QDialog.DialogCode.Accepted:
            model.setData(index, os.path.basename(str(editor.selectedFiles()[0])))
        os.chdir(self.oldwd)


class DateRowDelegate(QStyledItemDelegate):
    def __init__(
        self,
        minimum=QDate(),
        maximum=QDate.currentDate(),
        format="yyyy-MM-dd",
        parent=None,
    ):
        super(DateRowDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.format = format

    def createEditor(self, parent, option, index):
        dateedit = QDateEdit(parent)
        dateedit.setDateRange(self.minimum, self.maximum)
        dateedit.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        dateedit.setDisplayFormat(self.format)
        dateedit.setCalendarPopup(True)
        return dateedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setDate(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date())


class PlainTextRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(PlainTextRowDelegate, self).__init__(parent)

    def createEditor(self, parent, option, index):
        lineedit = QLineEdit(parent)
        return lineedit

    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        editor.setText(value)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.text().replace("(", "[").replace(")", "]"))


class RichTextRowDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super(RichTextRowDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.ItemDataRole.DisplayRole)
        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.StateFlag.State_Selected:
            document.setHtml("<font color={}>{}</font>".format(palette.highlightedText().color().name(), text))
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
