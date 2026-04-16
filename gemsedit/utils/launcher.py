"""
GEMSedit: Environment Editor for GEMS (Graphical Environment Management System)
Copyright (C) 2021-2026 Travis L. Seymour, PhD

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

import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys

import typer

from gemsedit.session.version import __version__
from gemsedit.utils.apputils import get_resource

APP_NAME = "GEMSedit"
APP_ID = "com.travisseymour.gemsedit"

launcher_app = typer.Typer(help="Install or uninstall desktop launcher for GEMSedit.")


def get_executable_path() -> str:
    """Get the path to the gemsedit executable."""
    # If running from installed package, use the entry point
    if hasattr(sys, "frozen"):
        return sys.executable
    # Otherwise, find the gemsedit command
    gemsedit_cmd = shutil.which("gemsedit")
    if gemsedit_cmd:
        return gemsedit_cmd
    # Fallback: use python -m gemsedit.main
    return f"{sys.executable} -m gemsedit.main"


def get_icon_path(size: int = 256) -> Path:
    """Get the path to an app icon of the specified size."""
    try:
        return get_resource("images", "appicon", f"icon_{size}.png")
    except FileNotFoundError:
        # Fallback to any available icon
        return get_resource("images", "appicon", "appicon.png")


# =============================================================================
# Linux Implementation
# =============================================================================


def _linux_get_desktop_file_path() -> Path:
    """Get the path for the .desktop file on Linux."""
    return Path.home() / ".local" / "share" / "applications" / "gemsedit.desktop"


def _linux_get_icon_dest_path() -> Path:
    """Get the destination path for the icon on Linux."""
    icons_dir = Path.home() / ".local" / "share" / "icons" / "hicolor" / "256x256" / "apps"
    icons_dir.mkdir(parents=True, exist_ok=True)
    return icons_dir / "gemsedit.png"


def _linux_install() -> tuple[bool, str]:
    """Install desktop launcher on Linux."""
    try:
        # Copy icon to standard location
        icon_src = get_icon_path(256)
        icon_dest = _linux_get_icon_dest_path()
        shutil.copy2(icon_src, icon_dest)

        # Create .desktop file
        desktop_file = _linux_get_desktop_file_path()
        desktop_file.parent.mkdir(parents=True, exist_ok=True)

        exec_path = get_executable_path()

        desktop_content = f"""[Desktop Entry]
Version=1.0
Type=Application
Name={APP_NAME}
Comment=Environment Editor for GEMS (Graphical Environment Management System)
Exec={exec_path}
Icon={icon_dest}
Terminal=false
Categories=Development;Education;
StartupWMClass=gemsedit
"""
        desktop_file.write_text(desktop_content)
        desktop_file.chmod(0o755)

        # Update desktop database
        try:
            subprocess.run(
                ["update-desktop-database", str(desktop_file.parent)],
                capture_output=True,
                check=False,
            )
        except FileNotFoundError:
            pass  # Command not available, but launcher should still work

        return True, f"Launcher installed successfully.\n  Desktop file: {desktop_file}\n  Icon: {icon_dest}"

    except Exception as e:
        return False, f"Failed to install launcher: {e}"


def _linux_uninstall() -> tuple[bool, str]:
    """Uninstall desktop launcher on Linux."""
    messages = []
    success = True

    desktop_file = _linux_get_desktop_file_path()
    if desktop_file.exists():
        desktop_file.unlink()
        messages.append(f"Removed desktop file: {desktop_file}")
    else:
        messages.append(f"Desktop file not found: {desktop_file}")

    icon_file = _linux_get_icon_dest_path()
    if icon_file.exists():
        icon_file.unlink()
        messages.append(f"Removed icon: {icon_file}")
    else:
        messages.append(f"Icon not found: {icon_file}")

    # Update desktop database
    try:
        subprocess.run(
            ["update-desktop-database", str(desktop_file.parent)],
            capture_output=True,
            check=False,
        )
    except FileNotFoundError:
        pass

    return success, "\n".join(messages)


# =============================================================================
# macOS Implementation
# =============================================================================


def _macos_get_app_path() -> Path:
    """Get the path for the .app bundle on macOS."""
    return Path.home() / "Applications" / f"{APP_NAME}.app"


def _macos_install() -> tuple[bool, str]:
    """Install application stub on macOS."""
    try:
        app_path = _macos_get_app_path()
        contents_path = app_path / "Contents"
        macos_path = contents_path / "MacOS"
        resources_path = contents_path / "Resources"

        # Create directory structure
        macos_path.mkdir(parents=True, exist_ok=True)
        resources_path.mkdir(parents=True, exist_ok=True)

        exec_path = get_executable_path()

        # Create launcher script
        launcher_script = macos_path / "GEMSedit"
        launcher_content = f"""#!/bin/bash
exec {exec_path} "$@"
"""
        launcher_script.write_text(launcher_content)
        launcher_script.chmod(0o755)

        # Create Info.plist
        info_plist = contents_path / "Info.plist"
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleExecutable</key>
    <string>GEMSedit</string>
    <key>CFBundleIdentifier</key>
    <string>{APP_ID}</string>
    <key>CFBundleName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleDisplayName</key>
    <string>{APP_NAME}</string>
    <key>CFBundleVersion</key>
    <string>{__version__}</string>
    <key>CFBundleShortVersionString</key>
    <string>{__version__}</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleIconFile</key>
    <string>appicon</string>
    <key>LSMinimumSystemVersion</key>
    <string>10.13</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
"""
        info_plist.write_text(plist_content)

        # Copy icon (use PNG, macOS can use it directly in many cases)
        icon_src = get_icon_path(512)
        icon_dest = resources_path / "appicon.png"
        shutil.copy2(icon_src, icon_dest)

        # Also try to create an icns if we have the tools
        try:
            _macos_create_icns(resources_path)
        except Exception:
            pass  # PNG fallback will work

        return True, f"Application installed successfully.\n  Location: {app_path}"

    except Exception as e:
        return False, f"Failed to install application: {e}"


def _macos_create_icns(resources_path: Path) -> None:
    """Try to create an .icns file from PNG icons."""
    iconset_path = resources_path / "appicon.iconset"
    iconset_path.mkdir(exist_ok=True)

    # Map of iconset filenames to our icon sizes
    icon_mappings = [
        ("icon_16x16.png", 16),
        ("icon_16x16@2x.png", 32),
        ("icon_32x32.png", 32),
        ("icon_32x32@2x.png", 64),
        ("icon_128x128.png", 128),
        ("icon_128x128@2x.png", 256),
        ("icon_256x256.png", 256),
        ("icon_256x256@2x.png", 512),
        ("icon_512x512.png", 512),
    ]

    for iconset_name, size in icon_mappings:
        try:
            src = get_icon_path(size)
            shutil.copy2(src, iconset_path / iconset_name)
        except FileNotFoundError:
            pass

    # Convert to icns using iconutil
    icns_path = resources_path / "appicon.icns"
    result = subprocess.run(
        ["iconutil", "-c", "icns", str(iconset_path), "-o", str(icns_path)],
        capture_output=True,
    )

    # Clean up iconset
    shutil.rmtree(iconset_path, ignore_errors=True)

    if result.returncode != 0:
        raise RuntimeError("iconutil failed")


def _macos_uninstall() -> tuple[bool, str]:
    """Uninstall application stub on macOS."""
    app_path = _macos_get_app_path()

    if app_path.exists():
        shutil.rmtree(app_path)
        return True, f"Application removed successfully.\n  Removed: {app_path}"
    else:
        return True, f"Application not found: {app_path}"


# =============================================================================
# Windows Implementation
# =============================================================================


def _windows_get_shortcut_path() -> Path:
    """Get the path for the Start Menu shortcut on Windows."""
    start_menu = Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return start_menu / f"{APP_NAME}.lnk"


def _windows_get_icon_path() -> Path:
    """Get the path where we'll store the icon on Windows."""
    app_data = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
    icon_dir = app_data / "GEMSedit"
    icon_dir.mkdir(parents=True, exist_ok=True)
    return icon_dir / "gemsedit.ico"


def _windows_install() -> tuple[bool, str]:
    """Install Start Menu shortcut on Windows."""
    try:
        # Copy icon (we'll use PNG since we don't have an ICO)
        icon_src = get_icon_path(256)
        icon_dest = _windows_get_icon_path().with_suffix(".png")
        icon_dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(icon_src, icon_dest)

        shortcut_path = _windows_get_shortcut_path()
        exec_path = get_executable_path()

        # Use PowerShell to create the shortcut
        ps_script = f"""
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{exec_path}"
$Shortcut.WorkingDirectory = "{Path.home()}"
$Shortcut.Description = "Environment Editor for GEMS"
$Shortcut.IconLocation = "{icon_dest}"
$Shortcut.Save()
"""
        result = subprocess.run(
            ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return False, f"Failed to create shortcut: {result.stderr}"

        return True, f"Launcher installed successfully.\n  Shortcut: {shortcut_path}\n  Icon: {icon_dest}"

    except Exception as e:
        return False, f"Failed to install launcher: {e}"


def _windows_uninstall() -> tuple[bool, str]:
    """Uninstall Start Menu shortcut on Windows."""
    messages = []

    shortcut_path = _windows_get_shortcut_path()
    if shortcut_path.exists():
        shortcut_path.unlink()
        messages.append(f"Removed shortcut: {shortcut_path}")
    else:
        messages.append(f"Shortcut not found: {shortcut_path}")

    icon_path = _windows_get_icon_path().with_suffix(".png")
    if icon_path.exists():
        icon_path.unlink()
        messages.append(f"Removed icon: {icon_path}")
        # Try to remove the directory if empty
        try:
            icon_path.parent.rmdir()
        except OSError:
            pass

    return True, "\n".join(messages)


# =============================================================================
# CLI Commands
# =============================================================================


@launcher_app.command()
def install():
    """Install a desktop launcher for GEMSedit."""
    system = platform.system()

    typer.echo(f"Installing {APP_NAME} launcher for {system}...")

    if system == "Linux":
        success, message = _linux_install()
    elif system == "Darwin":
        success, message = _macos_install()
    elif system == "Windows":
        success, message = _windows_install()
    else:
        typer.echo(f"Unsupported platform: {system}", err=True)
        raise typer.Exit(1)

    if success:
        typer.echo(message)
        typer.echo(f"\n{APP_NAME} launcher installed successfully!")
    else:
        typer.echo(message, err=True)
        raise typer.Exit(1)


@launcher_app.command()
def uninstall():
    """Remove the desktop launcher for GEMSedit."""
    system = platform.system()

    typer.echo(f"Uninstalling {APP_NAME} launcher for {system}...")

    if system == "Linux":
        success, message = _linux_uninstall()
    elif system == "Darwin":
        success, message = _macos_uninstall()
    elif system == "Windows":
        success, message = _windows_uninstall()
    else:
        typer.echo(f"Unsupported platform: {system}", err=True)
        raise typer.Exit(1)

    if success:
        typer.echo(message)
        typer.echo(f"\n{APP_NAME} launcher uninstalled successfully!")
    else:
        typer.echo(message, err=True)
        raise typer.Exit(1)
