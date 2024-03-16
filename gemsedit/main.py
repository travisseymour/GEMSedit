import os
from pathlib import Path

import appdirs
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication, QSystemTrayIcon
from PySide6.QtCore import QCoreApplication, QSettings
import sys
import platform

import gemsedit


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

    gemsedit.CONFIG_PATH = Path(appdirs.user_config_dir(), 'GEMS')
    gemsedit.CONFIG_PATH.mkdir(exist_ok=True)
    gemsedit.LOG_PATH = Path(gemsedit.CONFIG_PATH, 'gems_run_log.txt')
    gemsedit.log.add(str(gemsedit.LOG_PATH), rotation="5 MB")

    try:
        print(f'GEMSedit app logging enabled at {gemsedit.LOG_PATH}')
        gemsedit.log.info(f'GEMSedit app logging enabled at {gemsedit.LOG_PATH}')
    except Exception as e:
        print(f'GEMSedit app logging to {gemsedit.LOG_PATH} failed: "{e}"')
        gemsedit.log.warning(f'GEMSedit app logging to {gemsedit.LOG_PATH} failed: "{e}"')

    tray = QSystemTrayIcon()

    # Run App
    # -------

    # NOTE: This import has to go here because the gemsedit.log and gemsedit.LOG_PATH need to already be set
    #       before the gems_edit module gets loaded or else these paths don't point to the right place.
    #       this is likely more of an issue with how gems is packaged.
    from gemsedit.session.gems_edit import GemsViews

    gems_views = GemsViews()
    gems_views.MainWindow.show()

    sys.exit(gemsedit.APPLICATION.exec())


if __name__ == "__main__":
    main()
