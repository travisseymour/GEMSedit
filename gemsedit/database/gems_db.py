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
import shutil

from PySide6.QtWidgets import QMessageBox

from gemsedit.session.version import __version__
from gemsedit.utils.apputils import get_resource


def new_database(yaml_db_file: Path, media_folder: Path) -> tuple:
    errors = []
    if yaml_db_file.is_file():
        answer = QMessageBox.question(
            None,
            "Overwrite Existing Environment File?",
            f"The GEMS environment file {str(yaml_db_file)} already exists. Overwrite it with a new empty environment?",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.No:
            return tuple(errors)

        # make backup

        try:
            old_yaml_text = yaml_db_file.read_text()
            Path(yaml_db_file.parent, yaml_db_file.name + ".bak").write_text(old_yaml_text)
        except Exception:
            ...

    # Create Base Environment

    try:
        media_folder.mkdir(exist_ok=True)
    except Exception as e:
        errors.append(f"Error making media folder at {media_folder} ('{e}').")
        return tuple(errors)

    yaml_text = Path(get_resource("DefaultEnv.yaml")).read_text()
    yaml_text = yaml_text.replace("Version: TEMP_VERSION", f"Version: {__version__}")
    yaml_text = yaml_text.replace("Name: TEMP_NAME", f"Name: {yaml_db_file.stem.replace(' ', '_')}")

    start = get_resource("images", "default_env", "DefaultStart.jpg")
    end = get_resource("images", "default_env", "DefaultEnd.jpg")
    overview = get_resource("images", "default_env", "DefaultOverview.jpg")

    for image in (start, end, overview):
        try:
            shutil.copy2(image, media_folder)
        except Exception as e:
            errors.append(f"Error copying {Path(image).name} to {media_folder.name} ('{e}').")

    try:
        yaml_db_file.write_text(yaml_text)
    except Exception as e:
        errors.append(f"Error trying to write new GEMS environment to {str(yaml_db_file)} ('{e}').")

    return tuple(errors)
