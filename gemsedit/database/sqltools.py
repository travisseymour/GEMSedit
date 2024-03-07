from typing import Optional, Union

from PySide6 import QtSql
from loguru import logger as log


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


def get_next_value(
    column_name: str, table_name: str, default: Optional[Union[int, float]] = None
) -> Optional[Union[int, float]]:
    """next-value implies that the value is numeric!"""
    last_value = get_last_value(column_name, table_name)
    if isinstance(last_value, (int, float)):
        return last_value + 1
    else:
        return default
