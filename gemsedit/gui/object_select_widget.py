"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2025 Travis L. Seymour, PhD

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

from gemsedit import log


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
        self.x1 = 0
        self.y1 = 0
        self.x2 = 0
        self.y2 = 0
        self.current_view = current_view
        self.current_obj = current_obj
        self.allow_selection = allow_selection
        self.view_pic = view_pic
        self.media_path = media_path
        self.clicks_allowed = False
        self.other_objects = []
        self.bgPic = None
        self._result: tuple = ()
        self._keep_result = False
        self.is_dragging = False
        self.msg = "Press ENTER to close this window."
        self.msg_position = QPoint(20, 20)
        # self.resize(640, 480)
        # self.move(1000, 500)

        if self.allow_selection:
            self.msg = "Drag to (re)select an object region. Press ENTER to submit."
        else:
            self.msg = "Press ENTER to close."
        # self.setStyleSheet("background-color: rgb(0, 0, 0);")
        QtCore.QTimer.singleShot(1000, self.allow_clicks)  # Avoids ghost click from objects ui

    def allow_clicks(self):
        if self.allow_selection:
            self.clicks_allowed = True

    def showEvent(self, event):
        # Set bgPic
        # (Id INT PRIMARY KEY UNIQUE, Name TEXT UNIQUE, Foreground TEXT, Background TEXT, Overlay TEXT)
        if self.current_view is not None:
            query = QtSql.QSqlQuery()
            query.prepare("SELECT * FROM views where Id = :viewid" + " order by RowOrder")
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

        # Load Object Coordinates
        query = QtSql.QSqlQuery()
        query.prepare("SELECT * FROM objects where Parent = :viewid" + " order by RowOrder")
        query.bindValue(":viewid", self.current_view)
        query.exec()
        if query.isActive():
            try:
                while next(query):
                    _id = query.value(0)
                    parent = query.value(1)
                    name = query.value(2)
                    left = query.value(3)
                    top = query.value(4)
                    width = query.value(5)
                    height = query.value(6)
                    visible = query.value(7)
                    takeable = query.value(8)
                    draggable = query.value(9)
                    if _id == self.current_obj:
                        self.x1 = left
                        self.y1 = top
                        self.x2 = left + width
                        self.y2 = top + height
                    else:
                        self.other_objects.append(
                            (
                                name,
                                left,
                                top,
                                width,
                                height,
                                visible,
                                takeable,
                                draggable,
                            )
                        )
            except:
                pass

        super().showEvent(event)

    def closeEvent(self, event):
        if not self._keep_result:
            self.x1 = self.y1 = self.x2 = self.y2 = None
        if self.x1 is None or self.x2 is None or self.y1 is None or self.y2 is None:
            self._result = ()
        else:
            self._result = (
                self.x1,
                self.y1,
                self.x2,
                self.y2,
                self.x2 - self.x1,
                self.y2 - self.y1,
            )
        self._keep_result = False
        super().closeEvent(event)

    def mouseReleaseEvent(self, event):
        if self.allow_selection and self.is_dragging:
            self.x2 = event.pos().x()
            self.y2 = event.pos().y()
            if self.x2 < self.x1:
                self.x1, self.x2 = self.x2, self.x1
            if self.y2 < self.y1:
                self.y1, self.y2 = self.y2, self.y1
            self.msg = "Drag to (re)select an object region. Press ENTER to submit."
            self.is_dragging = False
            self.setMouseTracking(False)
            self.update()

        super().mouseReleaseEvent(event)

    def mousePressEvent(self, event):
        if self.allow_selection and self.clicks_allowed:
            self.is_dragging = True
            self.setMouseTracking(True)
            self.x1 = event.pos().x()
            self.y1 = event.pos().y()
            self.x2 = None
            self.y2 = None
            self.msg = "Drag to (re)select an object region. Release to finish."
            self.update()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # handle obj selection
        if self.allow_selection and self.is_dragging:
            # selection being updated, save xy2
            self.x2 = event.pos().x()
            self.y2 = event.pos().y()
            if self.x2 < self.x1:
                a = self.x1
                b = self.x2
                self.x2 = a
                self.x1 = b
            if self.y2 < self.y1:
                a = self.y1
                b = self.y2
                self.y2 = a
                self.y1 = b
            self.update()

        super().mouseMoveEvent(event)

    def paintEvent(self, event):
        # setup painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        # draw image
        if self.bgPic:
            painter.drawPixmap(0, 0, QtGui.QPixmap(self.bgPic))  # for scaled: QPixmap(blah).scaled(size())

        if self.msg:
            painter.setFont(QtGui.QFont("Arial", 14))  # 'Decorative'
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

        # draw other objects
        if len(self.other_objects):
            line_width = 3
            font_size = QApplication.instance().font().pointSize()
            for param_list in self.other_objects:
                name, left, top, width, height, visible, takeable, draggable = param_list

                # Draw box
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

                # not available in PySide6!? trying the setAlpha method above ^^^
                # painter.setBackgroundMode(QtCore.Qt.MaskMode.TransparentMode)

                painter.setFont(QtGui.QFont("Arial", font_size))  # 'Decorative'

                rect = QtCore.QRect()
                rect.setRect(left, top, width, height)

                painter.drawRect(rect)

                # Draw Text
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, line_width))
                # painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignLeft,Name)
                tp = top - line_width
                if tp < font_size:
                    tp = top + height + (line_width * 2)

                painter.setPen(QtCore.Qt.GlobalColor.black)
                painter.setBackground(QtGui.QBrush(QtCore.Qt.GlobalColor.white))

                # not available in PySide6!
                # painter.setBackgroundMode(QtCore.Qt.MaskMode.OpaqueMode)
                line_color.setAlpha(255)

                painter.drawText(left + line_width, tp, name)

        super().paintEvent(event)

        # handle selection
        if self.x1 and self.y1 and self.x2 and self.y2:
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow, 4))
            rect = QtCore.QRect()
            rect.setRect(self.x1, self.y1, self.x2 - self.x1, self.y2 - self.y1)
            painter.drawRect(rect)

        # shutdown painter
        painter.end()

    def keyPressEvent(self, event):
        # a = (event.type())
        # b = (event.key())
        # c = (QtCore.QEvent.Type.KeyPress)
        # log.debug(f"{a=}, {b=}, {c=}")
        if event.key() in (QtCore.Qt.Key.Key_Return, QtCore.Qt.Key.Key_Enter):
            self.update()
            self._keep_result = True
            self.close()
            return
        if event.key() == QtCore.Qt.Key.Key_Escape:
            # cancel selection and close without changes
            self.x1 = self.y1 = self.x2 = self.y2 = None
            self._result = ()
            self._keep_result = False
            self.close()
            return

        super().keyPressEvent(event)
