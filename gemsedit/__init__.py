from pathlib import Path

from loguru import logger as log
from PySide6.QtCore import QSettings
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QWidget

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

# --- Font scaling ---
font_scale: float = 1.0
_base_font_size: int = 14


def scaled_size(base: int | float) -> int:
    """Return a font size scaled by the current font_scale factor."""
    return max(round(base * font_scale), 6)


def scale_widget_fonts(root_widget: QWidget) -> None:
    """Recursively scale fonts on root_widget and all its children.

    On the first call for each widget, the widget's current point size is
    stored in a Qt dynamic property ``_original_font_size``.  Subsequent
    calls reuse that stored value so that repeated scaling doesn't compound.
    """
    for widget in [root_widget] + root_widget.findChildren(QWidget):
        font = widget.font()
        original = widget.property("_original_font_size")
        if original is None:
            pt = font.pointSizeF()
            if pt > 0:
                original = pt
                widget.setProperty("_original_font_size", original)
        if original is not None and original > 0:
            font.setPointSizeF(original * font_scale)
            widget.setFont(font)


def set_app_font(font: QFont | None = None):
    global app_font, app_font_bold, dialog_font, _base_font_size

    if font is not None:
        _base_font_size = font.pointSize()

    sz = max(round(_base_font_size * font_scale), 8)

    app_font = QFont("Arial", sz)
    app_font_bold = QFont("Arial", sz)
    app_font_bold.setBold(True)
    dialog_font = QFont("Arial", sz)

    try:
        app = QApplication.instance()
        app.setFont(app_font)
        # Apply font to menus via stylesheet since they don't always respect app font
        font_family = app_font.family()
        font_size = max(sz, 14)  # Minimum size of 14 for menus
        # Combined stylesheet for menus and dark mode compatibility
        # Uses palette colors to properly support both light and dark system themes
        app_stylesheet = f"""
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

            /* Fix QTextEdit and QPlainTextEdit for dark mode */
            QTextEdit, QPlainTextEdit {{
                background-color: palette(base);
                color: palette(text);
            }}

            /* Fix QTableView for dark mode - ensure text is readable */
            QTableView {{
                background-color: palette(base);
                color: palette(text);
                alternate-background-color: palette(alternateBase);
            }}
            QTableView::item {{
                color: palette(text);
            }}
            QTableView::item:selected {{
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }}
            QHeaderView::section {{
                background-color: palette(button);
                color: palette(buttonText);
            }}

            /* Help/result text labels - use palette colors for dark mode compatibility */
            /* Inline stylesheets are cleared programmatically in param_select.py and settings.py */
            #xxHelpLabel, #resultLabel {{
                background-color: palette(base);
                color: palette(text);
                border: 1px solid palette(mid);
            }}

            /* Section header labels (light blue) - ensure readable dark text on colored bg */
            #label_3, #label_4, #label_7, #label_8, #label_13, #titleLabel {{
                background-color: rgb(102, 204, 255);
                color: #000000;
            }}

            /* Parameter highlight labels (orange) - ensure readable dark text */
            #xxparamLabel, #xxLabel {{
                background-color: rgb(255, 204, 102);
                color: #000000;
            }}
        """
        app.setStyleSheet(app_stylesheet)
        log.debug(f"Global app font changed to {app_font.styleName()} ({sz} pt, scale={font_scale:.1f})")
    except AttributeError:
        ...


def set_app_font_bold(font: QFont):
    global app_font_bold
    app_font_bold = font
