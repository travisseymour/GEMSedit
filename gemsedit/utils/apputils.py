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
import shlex
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


def launch_in_terminal(app_name: str, params: list[str] | None = None) -> None:
    """
    Launch an application in a new terminal window, completely detached from the parent process.

    Args:
        app_name: Name or path of the executable to launch.
        params: Optional list of arguments.
    """
    command_parts = [app_name]
    if params:
        command_parts += [str(param) for param in params]

    # Build the full command string with proper quoting for shell
    # shlex.quote handles spaces and special characters
    full_command = " ".join(shlex.quote(part) for part in command_parts)

    if OS == "Windows":
        # Windows: use 'start' to open a new cmd window
        subprocess.Popen(
            ["cmd", "/c", "start", "cmd", "/k", full_command],
            start_new_session=True,
        )
    elif OS == "Darwin":
        # macOS: use osascript to open Terminal.app with the command
        apple_script = f'tell application "Terminal" to do script "{full_command}"'
        subprocess.Popen(
            ["osascript", "-e", apple_script],
            start_new_session=True,
        )
    else:
        # Linux: try common terminal emulators in order of preference
        terminals = [
            ["gnome-terminal", "--", "bash", "-c", f"{full_command}; exec bash"],
            ["konsole", "-e", "bash", "-c", f"{full_command}; exec bash"],
            ["xfce4-terminal", "-e", f"bash -c '{full_command}; exec bash'"],
            ["xterm", "-e", f"bash -c '{full_command}; read -p \"Press Enter to close...\"'"],
        ]

        for terminal_cmd in terminals:
            try:
                subprocess.Popen(terminal_cmd, start_new_session=True)
                return
            except FileNotFoundError:
                continue

        # If no terminal found, just run without a terminal
        subprocess.Popen(
            command_parts,
            start_new_session=True,
        )
