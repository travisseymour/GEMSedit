import ast
import io
import re
import os

# import platform
# import shutil
# from pathlib import Path

from setuptools import find_packages, setup


# if platform.system() == 'Darwin' and platform.platform().split('-')[1].startswith('10.'):
#     qt_package = 'PySide2'
# else:
#     qt_package =  'PySide6'  # requires MacOS version 11 or higher

qt_package = "PySide6"

DEPENDENCIES = [
    "qtpy",
    qt_package,
    "gtts",
    "loguru",
    "pyyaml",
    "sqlite-utils",
    "Jinja2",
    "networkx",
    "jsonpickle",
]
EXCLUDE_FROM_PACKAGES = [
    "contrib",
    "docs",
    "tests*",
    "test*",
    "build",
    "epicpy.egg-info",
]

CURDIR = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(CURDIR, "ReadMe.md"), "r", encoding="utf-8") as f:
    README = f.read()

PYTHON_VERSION = ">=3.9.0,<3.12"


def get_version():
    main_file = os.path.join(CURDIR, "gemsedit", "session", "version.py")
    _version_re = re.compile(r"__version__\s+=\s+(?P<version>.*)")
    with open(main_file, "r", encoding="utf8") as f:
        match = _version_re.search(f.read())
        if match:
            version = match.group("version")
        else:
            raise ValueError(f"{str(main_file)} has invalid version format!")
    return str(ast.literal_eval(version))


setup(
    name="gemsedit",
    version=get_version(),
    author="Travis L. Seymour, PhD",
    author_email="nogard@ucsc.edu",
    description="GEMSedit: Editor for the Graphical Environment Management System (GEMS).",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/travisseymour/GEMSedit",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    # package_dir={"": "gemsedit"},
    include_package_data=True,
    package_data={"gemsedit": ["resources/*"]},
    keywords=[],
    scripts=[],
    entry_points={
        "gui_scripts": ["GEMSedit=gemsedit.main:main"],
    },
    zip_safe=False,
    install_requires=DEPENDENCIES,
    test_suite="",
    python_requires=PYTHON_VERSION,
    # license and classifier list:
    # https://pypi.org/pypi?%3Aaction=list_classifiers
    license="License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Natural Language :: English",
        "Topic :: Education",
        "Topic :: Scientific/Engineering",
    ],
    # vvv these 2 lines are required to pull in the resources' folder.
    #     I think essentially this causes setup.py to pull in ANYTHING you
    #     have added to git!
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
)
