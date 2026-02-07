"""
GEMSedit
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

from importlib.metadata import version
import os

import tomli


def get_version_from_pyproject():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "..", "pyproject.toml")
    try:
        with open(pyproject_path, "rb") as f:
            pyproject_data = tomli.load(f)
            return pyproject_data.get("project", {}).get("version", None)
    except (FileNotFoundError, OSError):
        return None


# Prefer pyproject.toml when available (development mode), otherwise use installed package version
__version__ = get_version_from_pyproject()
if __version__ is None:
    try:
        __version__ = version("gemsedit")
    except Exception:
        __version__ = "Unknown"
