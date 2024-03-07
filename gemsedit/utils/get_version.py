from loguru import logger as log
from pathlib import Path
from typing import Optional

from gemsedit.utils.apputils import get_resource

app_short_name = "GEMSedit"
app_long_name = "GEMS Editor"

VERSION: Optional[str] = None


def update_version():
    version = get_gemsedit_version()
    try:
        Path("..", "session", "version.py").write_text(f'__version__ = "{version}"\n')
        log.info(f"GEMSedit version updated to {version}.")
    except Exception as e:
        log.error(f'Error updating version: "{e}"')


def get_gemsedit_version() -> str:
    global VERSION

    if not VERSION:
        try:
            change_log_file = get_resource("changelog.txt")
            assert Path(change_log_file).is_file()
        except Exception as e:
            log.error(f"{e}")
            return "?.?.?"
        changes = Path(change_log_file).read_text().splitlines(keepends=False)
        changes = [aline.split(" : ")[1].strip() for aline in changes]
        major, minor, incremental = 1, 0, 0
        for change in reversed(changes):
            if change.lower().startswith("major:"):
                major += 1
                minor = 0
                incremental = 0
            elif change.lower().startswith("minor"):
                minor += 1
                incremental = 0
            else:
                incremental += 1
        VERSION = f"{major}.{minor}.{incremental}"

    return VERSION


if __name__ == "__main__":
    log.info("Attempting to update version of GEMSedit")
    update_version()
