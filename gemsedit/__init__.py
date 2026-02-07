from pathlib import Path

from loguru import logger as log
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

# if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
#     pathEX = Path(sys._MEIPASS)
# else:
#     pathEX = Path(__file__).parent


CONFIG_PATH: Path | None = None
LOG_PATH: Path | None = None

APPLICATION: QApplication | None = None
SETTINGS: QSettings | None = None

app_font: QFont | None = QFont("Arial", 12)
app_font_bold: QFont | None = QFont("Arial", 12)
app_font_bold.setBold(True)

dialog_font = QFont("Arial", 12)

app_short_name = "GEMSedit"
app_long_name = "GEMS Editor"


def set_app_font(font: QFont):
    global app_font
    app_font = font
    try:
        app = QApplication.instance()
        app.setFont(font)
        # Apply font to menus via stylesheet since they don't always respect app font
        font_family = font.family()
        font_size = max(font.pointSize(), 14)  # Minimum size of 14 for menus
        menu_stylesheet = f"""
            QMenuBar, QMenuBar::item, QMenu, QMenu::item {{
                font-family: "{font_family}";
                font-size: {font_size}pt;
            }}
            QMenuBar::item:selected {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}
            QMenu::item:selected {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}
        """
        app.setStyleSheet(menu_stylesheet)
        log.debug(f"Global app font changed to {font.styleName()} ({font.pointSize()} pt)")
    except AttributeError:
        ...


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
