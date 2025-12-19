# http://pastebin.com/Vaxg99P1

import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ClickableLabel(QLabel):
    """Normal label, but emits an event if the label is left-clicked.
    This version works with Qt Designer which will pass the parent widget
    and use setText() to set the text afterward.
    """

    singnal_clicked = Signal()  # emitted whenever this label is left-clicked

    # def __init__(self, text, parent=None):
    #     super(ClickableLabel, self).__init__(text, parent)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            """
        QLabel {text-decoration:none}
        QLabel:hover {color:white; background:grey;}
        """
        )
        self.setFixedSize(self.sizeHint())

    def mousePressEvent(self, event):
        if event.button() == 1:  # Qt.LeftButton:
            self.singnal_clicked.emit()


class ClickableLabel_Orig(QLabel):
    """Normal label, but emits an event if the label is left-clicked"""

    singnal_clicked = Signal()  # emitted whenever this label is left-clicked

    def __init__(self, parent=None):
        super(ClickableLabel_Orig, self).__init__(parent)
        self.setStyleSheet(
            """
        QLabel {text-decoration:none}
        QLabel:hover {color:white; background:grey;}
        """
        )
        self.setFixedSize(self.sizeHint())

    def mousePressEvent(self, event):
        if event.button() == 1:  # Qt.LeftButton:
            self.singnal_clicked.emit()


class HtmlLabel(QLabel):
    """
    Normal label, but 'text' is embedded in html, which makes the label
    emitting the 'linkActivated' signal on left-clicks
    """

    def __init__(self, text, parent=None):
        super().__init__(self.getHtml(text), parent)
        self.setStyleSheet("QLabel:hover {background:grey;}")
        self.setFixedSize(self.sizeHint())

    def getHtml(self, text):
        """Return text embedded in a html link tag"""

        return """<a style = "text-decoration:none" href="asdf">%s</a>""" % text


class View(QWidget):
    """Demonstration GUI to show use of ClickableLabel and HtmlLabel"""

    def __init__(self):
        super(View, self).__init__()
        self.setupUi()

    def setupUi(self):
        """Initialize the GUI with different types of clickable labels"""

        self.resize(550, 200)
        self.layoutGeneral = QHBoxLayout(self)
        self.layoutGeneral.setSpacing(50)
        self.layoutLabel = QVBoxLayout()
        self.layoutGeneral.addLayout(self.layoutLabel)
        self.layoutDisplay = QVBoxLayout()
        self.layoutGeneral.addLayout(self.layoutDisplay)

        self.labelDate = ClickableLabel_Orig("Date")
        self.labelName = ClickableLabel_Orig("Name")
        self.labelAuthorHtml = HtmlLabel("Author")

        self.labelDisplay = QLabel("Click on the labels on the left")

        self.layoutLabel.addWidget(self.labelDate)
        self.layoutLabel.addWidget(self.labelName)
        self.layoutLabel.addWidget(self.labelAuthorHtml)

        self.layoutDisplay.addWidget(self.labelDisplay)


class Controller(QObject):
    """Controls interaction between model and view"""

    def __init__(self):
        super(Controller, self).__init__()
        self.view = View()
        self.connectSignals()

    def start(self):
        """Start application"""

        self.view.show()

    def connectSignals(self):
        """Connect the clickable labels with the corresponding slot"""

        self.view.labelDate.singnal_clicked.connect(self.onClickableLabel)
        self.view.labelName.singnal_clicked.connect(self.onClickableLabel)
        self.view.labelAuthorHtml.linkActivated.connect(self.onClickableLabel)

    def onClickableLabel(self):
        """A label was clicked, show the text of the label in the display"""

        self.view.labelDisplay.setText("The label with the following text was clicked:\n" + self.sender().text())


def main():
    app = QApplication(sys.argv)
    controller = Controller()
    controller.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
