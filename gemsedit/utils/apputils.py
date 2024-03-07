import subprocess
import sys
from pathlib import Path
from typing import Optional

from loguru import logger as log

import platform

import warnings
from functools import wraps

from gemsedit import pathEX

OS = platform.system()


def frozen() -> bool:
    return getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS")


if frozen():
    log.level("INFO")


def addroot(currpath):
    main_file_location = Path(__file__).parent.absolute()
    return str(Path(main_file_location, currpath))


def ospath(path_str: str) -> str:
    if OS == "Windows":
        return str(Path(path_str).absolute())
    else:
        return path_str


def ignore_warnings(f):
    # https://stackoverflow.com/questions/879173
    @wraps(f)
    def inner(*args, **kwargs):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("ignore")
            response = f(*args, **kwargs)
        return response

    return inner


class add_path:
    """
    Creates A Context Manager For Temporarily Adding Directory To System Path.
    E.g., see https://stackoverflow.com/questions/17211078
    """

    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


def fjoin(*elements):
    return Path(pathEX, *elements).resolve()


def get_resource(*args) -> Path:
    base_folder = Path(pathEX, "resources").resolve()

    target_path = Path(base_folder, *args)
    if target_path.exists():
        return target_path
    else:
        raise FileNotFoundError(f'Unable to locate resource "{str(target_path)}"')


def is_installed_via_pipx(package_name: str) -> bool:
    result = subprocess.run(["pipx", "list"], capture_output=True, text=True)
    return package_name in result.stdout


def start_external_app(
    app_name: str, params: Optional[list[str]] = None, wait: bool = False
) -> list:
    command = [app_name]

    if params is not None and len(params):
        command += [str(param) for param in params]

    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if wait:
        process.wait()
        output = [aline for aline in process.stdout]
    else:
        output = []
    return output
