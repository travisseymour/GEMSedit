import sys
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    pathEX = Path(sys._MEIPASS)
else:
    pathEX = Path(__file__).parent

CONFIG_PATH: Optional[Path] = None
LOG_PATH: Optional[Path] = None

APPLICATION: Optional[QApplication] = None
SETTINGS: Optional[QSettings] = None

app_font: Optional[QFont] = None
app_font_bold: Optional[QFont] = None

dialog_font = QFont("Arial", 12)

app_short_name = "GEMSrun"
app_long_name = "GEMS Runner"


def set_app_font(font: QFont):
    global app_font
    app_font = font


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
