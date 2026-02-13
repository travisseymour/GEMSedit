"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2025 Travis L. Seymour, PhD

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import datetime
import os
from pathlib import Path
import sys

import appdirs
from PySide6.QtCore import QCoreApplication, QSettings
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import QApplication

import gemsedit
from gemsedit import log
from gemsedit.utils.apputils import frozen, get_resource

os.environ["OUTDATED_IGNORE"] = "1"


def main():
    # Setup App
    # ---------

    gemsedit.APPLICATION = QApplication(sys.argv)
    gemsedit.set_app_font(QFont("Arial", 14))
    gemsedit.SETTINGS = QSettings()

    # Set some global vars
    QCoreApplication.setOrganizationName("TravisSeymour")
    QCoreApplication.setOrganizationDomain("travisseymour.com")
    QCoreApplication.setApplicationName("GEMSedit")

    # gemsedit.APPLICATION.setWindowIcon(QIcon(str(get_resource("images", "Icon.png"))))
    app_icon = QIcon()
    for size in [16, 24, 32, 48, 64, 128, 256, 512]:
        try:
            icon_path = get_resource("images", "appicon", f"icon_{size}.png")
            app_icon.addFile(str(icon_path))
        except FileNotFoundError:
            log.warning(f"Problem adding app icon {str(icon_path)}")
    gemsedit.APPLICATION.setWindowIcon(app_icon)

    gemsedit.CONFIG_PATH = Path(appdirs.user_config_dir(), "GEMS")
    gemsedit.CONFIG_PATH.mkdir(exist_ok=True)
    gemsedit.LOG_PATH = Path(gemsedit.CONFIG_PATH, "gems_edit_log.txt")
    gemsedit.LOG_PATH.write_text("")
    gemsedit.log.add(str(gemsedit.LOG_PATH))

    if frozen():
        log.level("INFO")

    try:
        gemsedit.log.info(f"\n---------------{datetime.datetime.now().ctime()}---------------")
        gemsedit.log.info(f"GEMSedit app logging enabled at {gemsedit.LOG_PATH}")
    except Exception as e:
        gemsedit.log.warning(f'GEMSedit app logging to {gemsedit.LOG_PATH} failed: "{e}"')

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
