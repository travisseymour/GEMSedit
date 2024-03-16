import sys
from pathlib import Path
from typing import Optional

import appdirs
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from loguru import logger as log

if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    pathEX = Path(sys._MEIPASS)
else:
    pathEX = Path(__file__).parent

CONFIG_PATH = Path(appdirs.user_config_dir(), 'GEMS')
LOG_PATH = Path(CONFIG_PATH, 'gems_run_log.txt')
APPLICATION: Optional[QApplication] = None
SETTINGS: Optional[QSettings] = None

app_font: Optional[QFont] = None
app_font_bold: Optional[QFont] = None

dialog_font = QFont("Arial", 12)

app_short_name = "GEMSrun"
app_long_name = "GEMS Runner"

log.add(str(LOG_PATH), rotation="5 MB")


def set_app_font(font: QFont):
    global app_font
    app_font = font


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
