import os
from pathlib import Path

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QCoreApplication, QSettings
from loguru import logger as log
import sys
import platform

import gemsedit

from gemsedit.session.gems_edit import GemsViews

os.environ["OUTDATED_IGNORE"] = "1"
if platform.platform().split("-")[1].startswith("10."):
    os.environ["QT_MAC_WANTS_LAYER"] = "1"


def main():
    # Setup App
    # ---------

    # Set some global vars
    QCoreApplication.setOrganizationName("TravisSeymour")
    QCoreApplication.setOrganizationDomain("travisseymour.com")
    QCoreApplication.setApplicationName("GEMSedit")

    gemsedit.APPLICATION = QApplication(sys.argv)
    gemsedit.default_font = QFont("Arial", 12)
    gemsedit.SETTINGS = QSettings()

    tray = QSystemTrayIcon()


    log_folder = Path(Path.home(), "Documents", "GEMS")
    log_file = Path(log_folder, "gems_edit_log.txt")

    try:
        log_folder.mkdir(exist_ok=True)
        assert log_folder.is_dir()
        log_file.write_text("")
        log.add(log_file, level="INFO", backtrace=True, diagnose=True)
    except Exception as e:
        log.error(f"Unable to setup logging to {str(log_file)} ({e}).")

    # Run App
    # -------

    gems_views = GemsViews(log_path=log_file)
    gems_views.MainWindow.show()

    sys.exit(gemsedit.APPLICATION.exec())


if __name__ == "__main__":
    main()
