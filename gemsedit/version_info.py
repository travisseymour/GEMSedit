import datetime
from pathlib import Path
from typing import Optional

app_short_name = "GEMSrun"
app_long_name = "GEMS Runner"

VERSION: Optional[str] = None


def get_version():
    now = datetime.datetime.now()
    current_year = now.year
    month = now.month
    day = now.day
    hour = now.hour
    minute = now.minute

    # Format the components as needed
    formatted_version = f"{current_year}.{month}.{day}.{hour}{minute:02}"
    return formatted_version


if __name__ == '__main__':
    Path(Path(__file__).parent, 'session', 'version.py').write_text(
        '# [CURRENT_YEAR].[MONTH].[DAY].[HOUR][MINUTE]\n'
        f'__version__ = "{get_version()}"\n'
    )

    from gemsedit.session.version import __version__

    print(f'Upgraded {app_short_name} version to {__version__}')
