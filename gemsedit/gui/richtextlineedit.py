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

import platform
import sys
from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QTextCharFormat


class RichTextLineEdit(QtWidgets.QTextEdit):
    (
        Bold,
        Italic,
        Underline,
        StrikeOut,
        Monospaced,
        Sans,
        Serif,
        NoSuperOrSubscript,
        Subscript,
        Superscript,
    ) = range(10)

    def __init__(self, parent=None):
        super(RichTextLineEdit, self).__init__(parent)

        self.monofamily = "courier"
        self.sansfamily = "helvetica"
        self.seriffamily = "times"
        self.setLineWrapMode(QtWidgets.QTextEdit.LineWrapMode.NoWrap)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        fm = QtGui.QFontMetrics(self.font())
        h = int(fm.height() * (1.4 if platform.system() == "Windows" else 1.2))
        self.setMinimumHeight(h)
        self.setMaximumHeight(int(h * 1.2))
        self.setToolTip("Press <b>Ctrl+M</b> for the text effects menu and <b>Ctrl+K</b> for the color menu")

    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())

    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())

    def toggleBold(self):
        self.setFontWeight(
            QtGui.QFont.Weight.Normal if self.fontWeight() > QtGui.QFont.Weight.Normal else QtGui.QFont.Weight.Bold
        )

    def sizeHint(self):
        return QtCore.QSize(int(self.document().idealWidth()) + 5, self.maximumHeight())

    def minimumSizeHint(self):
        fm = QFontMetrics(self.font())
        return QtCore.QSize(fm.horizontalAdvance("WWWW"), self.minimumHeight())

    def contextMenuEvent(self, event):
        self.textEffectMenu()

    def keyPressEvent(self, event):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            handled = False
            if event.key() == QtCore.Qt.Key.Key_B:
                self.toggleBold()
                handled = True
            elif event.key() == QtCore.Qt.Key.Key_I:
                self.toggleItalic()
                handled = True
            elif event.key() == QtCore.Qt.Key.Key_K:
                self.colorMenu()
                handled = True
            elif event.key() == QtCore.Qt.Key.Key_M:
                self.textEffectMenu()
                handled = True
            elif event.key() == QtCore.Qt.Key.Key_U:
                self.toggleUnderline()
                handled = True
            if handled:
                event.accept()
                return
        if event.key() in (QtCore.Qt.Key.Key_Enter, QtCore.Qt.Key.Key_Return):
            # self.emit(SIGNAL("returnPressed()"))
            # self.returnPressed.emit()  # Only exists in QLineEdit...this "LineEdit" class derives from QTextEdit!
            # I believe this was so I could have access to RTF abilities.
            # There is no equivalent <https://doc.qt.io/qt-5/qplaintextedit.html>,
            # so I'm emitting nothing. tls
            event.accept()
        else:
            QtWidgets.QTextEdit.keyPressEvent(self, event)

    def colorMenu(self):
        pixmap = QtGui.QPixmap(22, 22)
        menu = QtWidgets.QMenu("Colour")
        for text, color in (
            ("&Black", QtCore.Qt.GlobalColor.black),
            ("B&lue", QtCore.Qt.GlobalColor.blue),
            ("Dark Bl&ue", QtCore.Qt.GlobalColor.darkBlue),
            ("&Cyan", QtCore.Qt.GlobalColor.cyan),
            ("Dar&k Cyan", QtCore.Qt.GlobalColor.darkCyan),
            ("&Green", QtCore.Qt.GlobalColor.green),
            ("Dark Gr&een", QtCore.Qt.GlobalColor.darkGreen),
            ("M&agenta", QtCore.Qt.GlobalColor.magenta),
            ("Dark Mage&nta", QtCore.Qt.GlobalColor.darkMagenta),
            ("&Red", QtCore.Qt.GlobalColor.red),
            ("&Dark Red", QtCore.Qt.GlobalColor.darkRed),
        ):
            color = QtGui.QColor(color)
            pixmap.fill(color)
            action = menu.addAction(QtGui.QIcon(pixmap), text, self.setColor)
            action.setData(color)
        self.ensureCursorVisible()
        menu.exec(self.viewport().mapToGlobal(self.cursorRect().center()))

    def setColor(self):
        action = self.sender()
        if action is not None and isinstance(action, QtGui.QAction):
            color = QtGui.QColor(action.data())
            if color.isValid():
                self.setTextColor(color)

    def textEffectMenu(self):
        format = self.currentCharFormat()
        menu = QtWidgets.QMenu("Text Effect")
        for text, shortcut, data, checked in (
            (
                "&Bold",
                "Ctrl+B",
                RichTextLineEdit.Bold,
                self.fontWeight() > QtGui.QFont.Weight.Normal,
            ),
            ("&Italic", "Ctrl+I", RichTextLineEdit.Italic, self.fontItalic()),
            ("Strike &out", None, RichTextLineEdit.StrikeOut, format.fontStrikeOut()),
            ("&Underline", "Ctrl+U", RichTextLineEdit.Underline, self.fontUnderline()),
            (
                "&Monospaced",
                None,
                RichTextLineEdit.Monospaced,
                format.fontFamily() == self.monofamily,
            ),
            (
                "&Serifed",
                None,
                RichTextLineEdit.Serif,
                format.fontFamily() == self.seriffamily,
            ),
            (
                "S&ans Serif",
                None,
                RichTextLineEdit.Sans,
                format.fontFamily() == self.sansfamily,
            ),
            (
                "&No super or subscript",
                None,
                RichTextLineEdit.NoSuperOrSubscript,
                format.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignNormal,
            ),
            (
                "Su&perscript",
                None,
                RichTextLineEdit.Superscript,
                format.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript,
            ),
            (
                "Subs&cript",
                None,
                RichTextLineEdit.Subscript,
                format.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript,
            ),
        ):
            action = menu.addAction(text, self.setTextEffect)
            if shortcut is not None:
                action.setShortcut(QtGui.QKeySequence(shortcut))
            action.setData(data)
            action.setCheckable(True)
            action.setChecked(checked)
        self.ensureCursorVisible()
        menu.exec(self.viewport().mapToGlobal(self.cursorRect().center()))

    def setTextEffect(self):
        action = self.sender()
        if action is not None and isinstance(action, QtGui.QAction):
            what = int(action.data())
            if what == RichTextLineEdit.Bold:
                self.toggleBold()
                return
            if what == RichTextLineEdit.Italic:
                self.toggleItalic()
                return
            if what == RichTextLineEdit.Underline:
                self.toggleUnderline()
                return
            format = self.currentCharFormat()
            if what == RichTextLineEdit.Monospaced:
                format.setFontFamily(self.monofamily)
            elif what == RichTextLineEdit.Serif:
                format.setFontFamily(self.seriffamily)
            elif what == RichTextLineEdit.Sans:
                format.setFontFamily(self.sansfamily)
            if what == RichTextLineEdit.StrikeOut:
                format.setFontStrikeOut(not format.fontStrikeOut())
            if what == RichTextLineEdit.NoSuperOrSubscript:
                format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignNormal)
            elif what == RichTextLineEdit.Superscript:
                format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSuperScript)
            elif what == RichTextLineEdit.Subscript:
                format.setVerticalAlignment(QTextCharFormat.VerticalAlignment.AlignSubScript)
            self.mergeCurrentCharFormat(format)

    def toSimpleHtml(self):
        html = ""
        black = QtGui.QColor(QtCore.Qt.GlobalColor.black)
        block = self.document().begin()
        while block.isValid():
            iterator = block.begin()
            while iterator != block.end():
                fragment = iterator.fragment()
                if fragment.isValid():
                    format = fragment.charFormat()
                    family = format.fontFamily()
                    color = format.foreground().color()
                    # text = QtCore.Qt.escape(fragment.text()) # depreciated
                    # text = QtCore.Qt.QString(fragment.text()).toHtmlEscaped()  # doesn't exist in pyside
                    # TODO: Turned Them all off: DEBUG ONLY!
                    import cgi

                    text = cgi.escape(fragment.text(), True)
                    if format.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSubScript:
                        text = "<sub>{}</sub>".format(text)
                    elif format.verticalAlignment() == QTextCharFormat.VerticalAlignment.AlignSuperScript:
                        text = "<sup>{}</sup>".format(text)
                    if format.fontUnderline():
                        text = "<u>{}</u>".format(text)
                    if format.fontItalic():
                        text = "<i>{}</i>".format(text)
                    if format.fontWeight() > QtGui.QFont.Weight.Normal:
                        text = "<b>{}</b>".format(text)
                    if format.fontStrikeOut():
                        text = "<s>{}</s>".format(text)
                    if color != black or family:
                        attribs = ""
                        if color != black:
                            attribs += ' color="{}"'.format(color.name())
                        if family:
                            attribs += ' face="{}"'.format(family)
                        text = "<font{}>{}</font>".format(attribs, text)
                    html += text
                iterator += 1
            block = block.next()
        return html


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    lineedit = RichTextLineEdit()
    lineedit.show()
    lineedit.setWindowTitle("RichTextEdit")
    app.exec()
    print(lineedit.toHtml())
    print()
    print(lineedit.toPlainText())
    print()
    print(lineedit.toSimpleHtml())
