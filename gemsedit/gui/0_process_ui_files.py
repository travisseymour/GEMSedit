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

import importlib
from importlib import util
from pathlib import Path
from shutil import which
import subprocess

from rich import print

"""
This converts .ui files to .py files for PyQt6, but to keep GIT history accurate,
I only want to process ui files that actually changed.

"""

def detect_qt_binding() -> tuple[str, str]:
    """Return (binding label, uic command) for an available Qt binding."""
    candidates = [
        ("PySide6", "pyside6-uic", "pyside6"),
        ("PyQt6", "pyuic6", "pyqt6"),
    ]
    for module_name, cli, label in candidates:
        if util.find_spec(module_name) is None:
            continue
        if which(cli) is None:
            continue
        try:
            importlib.import_module(module_name)
        except Exception:
            continue
        return label, cli
    raise RuntimeError("Expecting to find either PySide6 or PyQt6 (and matching *uic tool) on PATH.")

qt_type, uic_cmd = detect_qt_binding()

ui_files: list[Path] = list(Path().glob("*.ui"))

if not ui_files:
    print("[bold yellow]No ui files found...nothing to do.[/]")
    raise SystemExit(0)

print(f"[bold yellow]Checking {len(ui_files)} ui files for potential changes...[/]")

found_anything = False

for ui in ui_files:
    py = ui.with_suffix(".py")
    if not py.is_file() or ui.stat().st_mtime > py.stat().st_mtime:
        found_anything = True
        print(f"[cyan]Converting {ui.name} to {py.name}[/]")
        try:
            subprocess.run([uic_cmd, str(ui.resolve()), "-o", str(py.resolve())], check=True)
            print("\t[green]Success![/]")
        except Exception as e:
            print(f"\t[bold red]ERROR:[/] {e}")

if not found_anything:
    print("[bold yellow]All files up to date. Nothing done.[/]")

print("[bold yellow]Finished.[/]")
