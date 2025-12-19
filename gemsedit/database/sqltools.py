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

from PySide6 import QtSql

from gemsedit import log


def get_last_value(column_name: str, table_name: str):
    query = QtSql.QSqlQuery()
    sql = f"select {column_name} from {table_name} order by {column_name}"
    query.exec(sql)
    if query.isActive() and query.isSelect():
        if query.last():
            return query.value(0)
        else:
            return None
    else:
        log.error(f"Problem with SQL query '{sql}' (Error: {query.lastError().text()})")
        return None


def get_next_value(column_name: str, table_name: str, default: int | float | None = None) -> int | float | None:
    """next-value implies that the value is numeric!"""
    last_value = get_last_value(column_name, table_name)
    if isinstance(last_value, (int, float)):
        return last_value + 1
    else:
        return default
