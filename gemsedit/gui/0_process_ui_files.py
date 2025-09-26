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

from pathlib import Path
from typing import List

from plumbum.colors import cyan, yellow, red, green, bold
from plumbum import local

"""
This converts .ui files to .py files for PyQt6, but to keep GIT history accurate, 
I only want to process ui files that actually changed.

After running this, files that try to import the _rc file may need this line added:

import gemsedit.gui.gemsedit_rc  # noqa: F401

the comment prevents black and ruff from deleting it!
"""

try:
    qt_type = "pyside6"
except:
    qt_type = ""

if not qt_type:
    try:
        qt_type = "pyqt6"
    except:
        qt_type = "???"
        raise ValueError("Expecting To Find Either PySide6 or PyQt6!")


ui_files: List[Path] = list(Path().glob("*.ui"))

if not ui_files:
    print("No ui files found...nothing to do." | yellow & bold)

print(f"Checking {len(ui_files)} ui files for potential changes..." | yellow & bold)

found_anything = False

for ui in ui_files:
    py = ui.with_suffix(".py")
    if not py.is_file() or ui.stat().st_mtime > py.stat().st_mtime:
        found_anything = True
        print(f"Converting {ui.name} to {py.name}" | cyan)
        try:
            local["pyuic6" if qt_type == "pyqt6" else "pyside6-uic"]([str(ui.resolve()), "-o", str(py.resolve())])
            print("\tSuccess!" | green)
        except Exception as e:
            print(f"\tERROR: {e}" | red & bold)

if not found_anything:
    print("All files up to date. Nothing done." | yellow & bold)

print("Finished." | yellow & bold)
