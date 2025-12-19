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
from tempfile import TemporaryDirectory

from PySide6.QtSql import QSqlDatabase
from PySide6.QtWidgets import QMessageBox
import yaml

from gemsedit.database.yamlsqlexchange import (
    dict_to_sqlite_file,
    load_yaml_as_dict,
    sqlite_to_dict,
)
from gemsedit.session.version import __version__

# https://qt.gitorious.org/pyside/pyside-examples/source/060dca8e4b82f301dfb33a7182767eaf8ad3d024:examples/sql/connection.py
# http://qt-project.org/doc/qt-5/qtsql-books-bookwindow-cpp.html <<- check if qsqlite driver exists


DB_CHANGED: bool = False


def mark_db_as_changed():
    global DB_CHANGED
    DB_CHANGED = True


class GemsDB:
    def __init__(self):
        self.db: QSqlDatabase | None = None
        self.tmp_folder = TemporaryDirectory()
        self.tmp_file = None
        self.yaml_file_name = None
        self.ui_list_yaml_file = None

    def __del__(self):
        try:
            self.close_db(offer_to_save_changes=False)
        except:
            ...

        try:
            self.tmp_folder.cleanup()
        except:
            ...

    def db_opened(self):
        try:
            assert self.db.isOpen()
            assert self.db.isValid()
            assert self.tmp_file
            assert self.yaml_file_name
            return True
        except (AttributeError, AssertionError):
            return False

    @staticmethod
    def db_changed() -> bool:
        return DB_CHANGED

    def open_db(
        self,
        db_yaml_file: Path | str,
        ui_list_yaml_file: Path | str | None = None,
    ) -> bool:
        global DB_CHANGED
        if self.db_opened():
            self.close_db()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.yaml_file_name = str(db_yaml_file)
        self.ui_list_yaml_file = str(ui_list_yaml_file)
        db_as_dict = load_yaml_as_dict(db_yaml_file, extra_yaml=ui_list_yaml_file)
        self.tmp_file = Path(self.tmp_folder.name, "gems_sqlite_temp.db")

        tmp_db_in_sqlite_file = dict_to_sqlite_file(db_as_dict, self.tmp_file, overwrite=True)
        self.db.setDatabaseName(str(tmp_db_in_sqlite_file))
        self.db.open()
        DB_CHANGED = False

        if self.db_opened():
            return True
        else:
            self.close_db(offer_to_save_changes=False)
            return False

    def __save_db_to_yaml(self, sqlite_db_file: Path | str, confirm: bool = True):
        global DB_CHANGED

        if sqlite_db_file is None or str(sqlite_db_file).strip() == "None":
            return

        if confirm:
            answer = QMessageBox.question(
                None,
                "Save Changes?",
                f"Save Environment Changes To {self.yaml_file_name}?",
                QMessageBox.StandardButton.Yes,
                QMessageBox.StandardButton.No,
            )
        else:
            answer = QMessageBox.StandardButton.Yes

        if answer == QMessageBox.StandardButton.Yes:
            problems = list()
            # convert db to dict representation first
            try:
                db_as_dict = sqlite_to_dict(sqlite_db_file, Path(self.yaml_file_name).stem)
            except Exception as e:
                db_as_dict = {}
                problems.append(f"- Problem saving internal sqlite db to dict prior to saving as yaml file: {e}")

            if not problems:
                # strip off ui tables
                try:
                    for ui_table_name in ("action_lst", "condition_lst", "trigger_lst"):
                        del db_as_dict[ui_table_name]
                except Exception as e:
                    problems.append(f"- Problem removing ui table lists from db before save: {e}")

                # update version
                try:
                    db_as_dict["Global"]["Options"]["Version"] = __version__
                except Exception as e:
                    problems.append(f"- Problem updating GEMSedit version number before save: {e}")

                # save it now
                try:
                    with open(self.yaml_file_name, "w") as outfile:
                        yaml.dump(db_as_dict, outfile, default_flow_style=False)
                except Exception as e:
                    problems.append(f"- Problem saving yaml file to disk: {e}")

            if problems:
                endl = "\n"
                _ = QMessageBox.critical(
                    None,
                    "Environment Save Error",
                    f"Error while trying to save environment to {self.yaml_file_name}:{endl.join(problems)}",
                    QMessageBox.StandardButton.Ok,
                )
            else:
                DB_CHANGED = False

    def save_db(self):
        self.__save_db_to_yaml(self.tmp_file, confirm=False)

    def close_db(self, offer_to_save_changes: bool = True):
        if offer_to_save_changes:
            self.__save_db_to_yaml(self.tmp_file)

        if self.db_opened():
            self.db.close()

        self.tmp_file = None
        self.yaml_file_name = None
        self.ui_list_yaml_file = None
        self.db = None
