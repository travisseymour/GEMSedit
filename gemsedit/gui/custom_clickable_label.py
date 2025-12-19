import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QVBoxLayout, QWidget


class ClickableLabel(QLabel):
    """Normal label, but emits an event if the label is left-clicked.
    This version works with Qt Designer which will pass the parent widget
    and use setText() to set the text afterward.
    """

    signal_clicked = Signal()  # emitted whenever this label is left-clicked

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
            self.signal_clicked.emit()


class ClickableLabelOrig(QLabel):
    """Normal label, but emits an event if the label is left-clicked"""

    signal_clicked = Signal()  # emitted whenever this label is left-clicked

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
            self.signal_clicked.emit()


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

        return f"""<a style = "text-decoration:none" href="asdf">{text}</a>"""


class View(QWidget):
    """Demonstration GUI to show use of ClickableLabel and HtmlLabel"""

    def __init__(self):
        super().__init__()
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

        self.labelDate = ClickableLabelOrig("Date")
        self.labelName = ClickableLabelOrig("Name")
        self.labelAuthorHtml = HtmlLabel("Author")

        self.labelDisplay = QLabel("Click on the labels on the left")

        self.layoutLabel.addWidget(self.labelDate)
        self.layoutLabel.addWidget(self.labelName)
        self.layoutLabel.addWidget(self.labelAuthorHtml)

        self.layoutDisplay.addWidget(self.labelDisplay)


class Controller(QObject):
    """Controls interaction between model and view"""

    def __init__(self):
        super().__init__()
        self.view = View()
        self.connectSignals()

    def start(self):
        """Start application"""

        self.view.show()

    def connectSignals(self):
        """Connect the clickable labels with the corresponding slot"""

        self.view.labelDate.signal_clicked.connect(self.onClickableLabel)
        self.view.labelName.signal_clicked.connect(self.onClickableLabel)
        self.view.labelAuthorHtml.linkActivated.connect(self.onClickableLabel)

    def onClickableLabel(self):
        """A label was clicked, show the text of the label in the display"""
        sender = self.sender()
        text = sender.text() if sender and callable(getattr(sender, "text", None)) else ""

        self.view.labelDisplay.setText("The label with the following text was clicked:\n" + text)


def main():
    app = QApplication(sys.argv)
    controller = Controller()
    controller.start()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
