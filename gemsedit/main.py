import os

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QCoreApplication, QSettings
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

    # Run App
    # -------

    gems_views = GemsViews()
    gems_views.MainWindow.show()

    sys.exit(gemsedit.APPLICATION.exec())


if __name__ == "__main__":
    main()
