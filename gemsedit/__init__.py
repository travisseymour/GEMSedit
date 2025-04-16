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

# NOTE: This vvv import is not used here, but must be here for reference from other modules!
from loguru import logger as log

CONFIG_PATH: Optional[Path] = None
LOG_PATH: Optional[Path] = None

APPLICATION: Optional[QApplication] = None
SETTINGS: Optional[QSettings] = None

app_font: Optional[QFont] = QFont("Arial", 12)
app_font_bold: Optional[QFont] = QFont("Arial", 12)
app_font_bold.setBold(True)

dialog_font = QFont("Arial", 12)

app_short_name = "GEMSrun"
app_long_name = "GEMS Runner"


def set_app_font(font: QFont):
    global app_font
    app_font = font
    try:
        QApplication.instance().setFont(font)
    except AttributeError:
        ...


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
