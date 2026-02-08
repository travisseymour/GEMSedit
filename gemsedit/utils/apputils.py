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

from importlib.resources import as_file, files
from pathlib import Path
import platform
import subprocess
import sys

OS = platform.system()


def frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


def get_resource(*args: str, project: str = "gemsedit") -> Path:
    """
    Constructs and returns the full absolute path to a resource within '[PROJECT]/resources'.

    Args:
        *args: A sequence of strings representing the relative path components
               within '[PROJECT]/resources', e.g., ("other", "devices.zip").

    Returns:
        pathlib.Path: An absolute Path object pointing to the resource that works
                      during development and when packaged.

    Raises:
        FileNotFoundError: If the resource does not exist.
        RuntimeError: If an error occurs while resolving the resource path.
    """
    try:
        # Base directory for resources in the package
        base = files(project).joinpath("resources")

        # Construct the resource path relative to the base
        resource_path = base.joinpath(*args)

        # Ensure the resource path is accessible as a file
        with as_file(resource_path) as resolved_path:
            return Path(resolved_path).resolve()  # Ensure the path is absolute
    except FileNotFoundError:
        raise FileNotFoundError(f"Resource not found: {'/'.join(args)}") from FileNotFoundError
    except Exception as e:
        raise RuntimeError(f"Error accessing resource: {e}") from Exception


def start_external_app(app_name: str, params: list[str] | None = None, wait: bool = False) -> list[str]:
    """
    Launch an external executable and optionally return its stdout output.

    Args:
        app_name: Name or path of the executable to launch.
        params: Optional list of arguments.
        wait: When True, wait for the process to finish and return its stdout lines as str.

    Returns:
        List of stdout lines (strings) if wait is True, otherwise an empty list.
    """
    command = [app_name]

    if params:
        command += [str(param) for param in params]

    # start_new_session=True detaches the child process from the parent's process group,
    # preventing crashes in the child from affecting the parent
    # text=True ensures we always get strings from stdout/stderr instead of bytes
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        start_new_session=True,
    )
    if wait:
        process.wait()
        output = [aline.rstrip("\n") for aline in process.stdout]
    else:
        output = []
    return output
