from typing import Any

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QFont


class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)

    @staticmethod
    def question(
        parent,
        title: str,
        text: str,
        font: QFont,
        buttons: Any = None,
        default_button: Any = None,
    ):
        """
        Custom question message box with font and icon.
        Args:
            parent
            title (str): Title of the message box.
            text (str): Main text of the message box.
            font (QFont): Custom font for the message box.
            buttons (Any): Custom buttons
            default_button (Any): Default button

        Returns:
            int: Standard button clicked (e.g., QMessageBox.Yes or QMessageBox.No).
        """
        box = CustomMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setFont(font)
        box.setIcon(QMessageBox.Question)
        if buttons is not None:
            box.setStandardButtons(buttons)
        else:
            box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        if default_button is not None:
            box.setDefaultButton(default_button)
        else:
            box.setDefaultButton(QMessageBox.No)
        return box.exec()

    @staticmethod
    def critical(parent, title: str, text: str, font: QFont, buttons: Any = None):
        """
        Custom critical message box with font and icon.
        Args:
            parent
            title (str): Title of the message box.
            text (str): Main text of the message box.
            font (QFont): Custom font for the message box.
            buttons (Any):

        Returns:
            int: Standard button clicked (e.g., QMessageBox.Ok).
        """
        box = CustomMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setFont(font)
        box.setIcon(QMessageBox.Critical)
        box.setStandardButtons(QMessageBox.Ok)
        box.setDefaultButton(QMessageBox.Ok)
        return box.exec()

    @staticmethod
    def information(parent, title: str, text: str, font: QFont, buttons: Any = None):
        """
        Custom information message box with font and icon.
        Args:
            parent
            title (str): Title of the message box.
            text (str): Main text of the message box.
            font (QFont): Custom font for the message box.
            buttons (Any):

        Returns:
            int: Standard button clicked (e.g., QMessageBox.Ok).
        """
        box = CustomMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setFont(font)
        box.setIcon(QMessageBox.Information)
        box.setStandardButtons(QMessageBox.Ok)
        box.setDefaultButton(QMessageBox.Ok)
        return box.exec()

    @staticmethod
    def warning(parent, title: str, text: str, font: QFont, buttons: Any = None):
        """
        Custom information message box with font and icon.
        Args:
            title (str): Title of the message box.
            text (str): Main text of the message box.
            font (QFont): Custom font for the message box.
            buttons (Any):

        Returns:
            int: Standard button clicked (e.g., QMessageBox.Ok).
        """
        box = CustomMessageBox(parent)
        box.setWindowTitle(title)
        box.setText(text)
        box.setFont(font)
        box.setIcon(QMessageBox.Warning)
        box.setStandardButtons(QMessageBox.Ok)
        box.setDefaultButton(QMessageBox.Ok)
        return box.exec()


# Example usage:
if __name__ == "__main__":
    import sys

    from PySide6.QtWidgets import QWidget

    class MainWin(QWidget):
        def __init__(self):
            super().__init__()

            # Custom font
            customFont = QFont("Arial", 12)

            # Create custom question message box
            result = CustomMessageBox.question(
                None,
                "Custom Question",
                "Are you sure you want to proceed?",
                font=customFont,
            )
            print("Question result:", result)

            # Create custom critical message box
            result = CustomMessageBox.critical(
                None,
                "Custom Critical",
                "An error occurred. Please try again later.",
                font=customFont,
            )
            print("Critical result:", result)

            # Create custom info message box
            result = CustomMessageBox.information(
                None,
                "Custom Info",
                "You have done a good job here!",
                font=customFont,
            )
            print("Info result:", result)

            # Create custom warn message box
            result = CustomMessageBox.warning(
                None,
                "Custom Warning",
                "NOTICE: Duplicated Info Won't be Saved.",
                font=customFont,
            )
            print("Info result:", result)

            self.setWindowTitle("CLOSE ME!")
            self.show()

    app = QApplication(sys.argv)

    main_win = MainWin()

    sys.exit(app.exec())
