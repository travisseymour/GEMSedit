from PySide6 import QtCore, QtGui, QtWidgets, QtSql
import os

from PySide6.QtCore import QPoint
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
        super(ObjectSelect, self).__init__(parent)
        self.x1 = self.y1 = self.x2 = self.y2 = 0
        self.current_view = current_view
        self.current_obj = current_obj
        self.allow_selection = allow_selection
        self.view_pic = view_pic
        self.media_path = media_path
        self.clicks_allowed = False
        self.other_objects = []
        self.bgPic = None
        self.result = None
        self.msg = "Press ENTER to close this window."
        self.msg_position = QPoint(20, 20)
        # self.resize(640, 480)
        # self.move(1000, 500)

        if self.allow_selection:
            self.msg = "Single Click to begin object selection. Press ENTER to submit."
        else:
            self.msg = "Press ENTER to close."
        # self.setStyleSheet("background-color: rgb(0, 0, 0);")
        QtCore.QTimer.singleShot(
            1000, self.allow_clicks
        )  # Avoids ghost click from objects ui

    def allow_clicks(self):
        if self.allow_selection:
            self.clicks_allowed = True

    def showEvent(self, event):
        # Set bgPic
        # (Id INT PRIMARY KEY UNIQUE, Name TEXT UNIQUE, Foreground TEXT, Background TEXT, Overlay TEXT)
        if self.current_view is not None:
            query = QtSql.QSqlQuery()
            query.prepare(
                "SELECT * FROM views where Id = :viewid" + " order by RowOrder"
            )
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
                    log.error(
                        "Error in objects.showEvent(): viewpic is invalid or associated file is unreadable."
                    )
                    return

        # Load Object Coordinates
        query = QtSql.QSqlQuery()
        query.prepare(
            "SELECT * FROM objects where Parent = :viewid" + " order by RowOrder"
        )
        query.bindValue(":viewid", self.current_view)
        query.exec()
        if query.isActive():
            try:
                while next(query):
                    Id = query.value(0)
                    Parent = query.value(1)
                    Name = query.value(2)
                    Left = query.value(3)
                    Top = query.value(4)
                    Width = query.value(5)
                    Height = query.value(6)
                    Visible = query.value(7)
                    Takeable = query.value(8)
                    Draggable = query.value(9)
                    if Id == self.current_obj:
                        self.x1 = Left
                        self.y1 = Top
                        self.x2 = Left + Width
                        self.y2 = Top + Height
                    else:
                        self.other_objects.append(
                            (
                                Name,
                                Left,
                                Top,
                                Width,
                                Height,
                                Visible,
                                Takeable,
                                Draggable,
                            )
                        )
            except:
                pass

        super(ObjectSelect, self).showEvent(event)

    def closeEvent(self, event):
        if self.x1 is None or self.x2 is None or self.y1 is None or self.y2 is None:
            self.result = None
        else:
            self.result = (
                self.x1,
                self.y1,
                self.x2,
                self.y2,
                self.x2 - self.x1,
                self.y2 - self.y1,
            )
        super(ObjectSelect, self).closeEvent(event)

    def mouseReleaseEvent(self, event):
        if self.allow_selection and self.clicks_allowed:
            self.setMouseTracking(not self.hasMouseTracking())
            if self.hasMouseTracking():
                # selection started, save xy1
                self.x1 = event.pos().x()
                self.y1 = event.pos().y()
                self.x2 = None
                self.y2 = None
                self.msg = "Mouse tracking is on. Move mouse to select object. Single click to end selection."
            else:
                # selection ended, show result
                self.msg = (
                    "Single Click to begin object selection. Press ENTER to submit."
                )
            self.update()

        super(ObjectSelect, self).mouseReleaseEvent(event)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        # handle obj selection
        if self.allow_selection:
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

        super(ObjectSelect, self).mouseMoveEvent(event)

    def paintEvent(self, event):
        # http://zetcode.com/gui/pysidetutorial/drawing/

        # setup painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing, True)

        # draw image
        if self.bgPic:
            # http://goo.gl/bbBNQ6
            painter.drawPixmap(
                0, 0, QtGui.QPixmap(self.bgPic)
            )  # for scaled: QPixmap(blah).scaled(size())

        if self.msg:
            painter.setFont(QtGui.QFont("Arial", 14))  # 'Decorative'
            painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.yellow))
            painter.drawText(self.msg_position, self.msg)

        # draw other objects
        if len(self.other_objects):
            line_width = 3
            fontsize = 12
            for param_list in self.other_objects:
                Name, Left, Top, Width, Height, Visible, Takeable, Draggable = (
                    param_list
                )

                # Draw box
                if Takeable:
                    line_color = QtGui.QColor("green")
                else:
                    line_color = QtGui.QColor("red")

                line_color.setAlpha(128)

                if Visible:
                    line_type = QtCore.Qt.PenStyle.SolidLine
                else:
                    line_type = QtCore.Qt.PenStyle.DotLine

                painter.setPen(QtGui.QPen(line_color, line_width, line_type))

                # not available in PySide6!? trying the setAlpha method above ^^^
                # painter.setBackgroundMode(QtCore.Qt.MaskMode.TransparentMode)

                painter.setFont(QtGui.QFont("Arial", fontsize))  # 'Decorative'

                rect = QtCore.QRect()
                rect.setRect(Left, Top, Width, Height)

                painter.drawRect(rect)

                # Draw Text
                painter.setPen(QtGui.QPen(QtCore.Qt.GlobalColor.white, line_width))
                # painter.drawText(rect, QtCore.Qt.AlignmentFlag.AlignLeft,Name)
                tp = Top - line_width
                if tp < fontsize:
                    tp = Top + Height + (line_width * 2)

                painter.setPen(QtCore.Qt.GlobalColor.black)
                painter.setBackground(QtGui.QBrush(QtCore.Qt.GlobalColor.white))

                # not available in PySide6!
                # painter.setBackgroundMode(QtCore.Qt.MaskMode.OpaqueMode)
                line_color.setAlpha(255)

                painter.drawText(Left + line_width, tp, Name)

        super(ObjectSelect, self).paintEvent(event)

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
        if (
            event.type() == QtCore.QEvent.Type.KeyPress and event.key() == 16777220
        ):  # QtCore.Qt.Key_Enter):
            self.update()
            self.close()
            # return True
        else:
            QtWidgets.QWidget.keyPressEvent(self, event)

        super(ObjectSelect, self).keyPressEvent(event)
