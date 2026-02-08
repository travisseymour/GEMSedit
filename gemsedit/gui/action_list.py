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

import re

from PySide6 import QtCore, QtGui, QtSql, QtWidgets
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from gemsedit import log
from gemsedit.database.connection import mark_db_as_changed

# from html import escape
from gemsedit.database.sqltools import get_next_value
import gemsedit.gui.genericcoldelegates as generic_col_delegates


def getHumanReadableFromId(table, _id):
    if table == "views":
        query = QtSql.QSqlQuery()
        query.exec(f"select Name from views where Id = {_id}")
        if query.isActive():
            query.first()
            view_name = query.value(0)
            return f'"{_id}:{view_name}"'
    elif table == "objects":
        view_names = {}
        query = QtSql.QSqlQuery()
        query.exec("select Id, Name from views")
        if query.isActive():
            while next(query):
                view_id = query.value(0)  # id
                view_name = query.value(1)  # Name
                view_names[str(view_id)] = str(view_name)
        query2 = QtSql.QSqlQuery()
        query2.exec(f"select Parent, Name from objects where Id = {_id}")
        if query2.isActive():
            query2.first()
            parent_view_id = query2.value(0)
            object_name = query2.value(1)
            parent_view_name = view_names[str(parent_view_id)]
            return f'"{_id}:{parent_view_name}:{object_name}"'
    else:
        return None


def actionComponentById(component, _id):
    query = QtSql.QSqlQuery()
    query.exec(f"select {component} from actions where Id = {_id}")
    if not query.lastError().isValid():
        query.first()
        return query.value(0)
    else:
        return None


class CustomSqlModel2(QtSql.QSqlQueryModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._signal_update = None
        self.problem = {}

    def initSignal(self, signal_update=None):
        if signal_update is not None:
            self._signal_update = signal_update

    def data(self, item: QtCore.QModelIndex, role: int = QtCore.Qt.ItemDataRole.DisplayRole):  # was role: int = ...
        value = super().data(item, role)
        # if role == QtCore.Qt.ItemDataRole.TextColorRole and index.column() == 0:
        #     return QtGui.QColor(QtCore.Qt.GlobalColor.blue)
        if role == QtCore.Qt.ItemDataRole.BackgroundRole:
            condition_index = self.index(item.row(), 3)
            condition = self.data(condition_index, QtCore.Qt.ItemDataRole.DisplayRole)
            trigger_index = self.index(item.row(), 4)
            trigger = self.data(trigger_index, QtCore.Qt.ItemDataRole.DisplayRole)
            action_index = self.index(item.row(), 5)
            action = self.data(action_index, QtCore.Qt.ItemDataRole.DisplayRole)
            if (condition == trigger == action == "") or (condition is trigger is action is None):
                self.problem[str(item.row())] = "Error: Row is completely blank."
            elif (condition != "" and condition is not None) and (
                (trigger == "" or trigger is None) or (action == "" or action is None)
            ):
                self.problem[str(item.row())] = "Error: Row has a condition, but lacks a trigger or action."
            elif (action == "" or action is None) and (trigger != "" and trigger is not None):
                self.problem[str(item.row())] = "Error: Row has a trigger, but lacks an action."
            elif (trigger == "" or trigger is None) and (action != "" and action is not None):
                self.problem[str(item.row())] = "Error: Row has an action, but no trigger."
            else:
                self.problem[str(item.row())] = ""
            if self.problem[str(item.row())] != "":
                return QtGui.QColor(255, 180, 180)  # Light red

        if role == QtCore.Qt.ItemDataRole.ForegroundRole:
            # Gray text for disabled rows, black for enabled
            enabled_index = self.index(item.row(), 6)
            enabled = super().data(enabled_index, QtCore.Qt.ItemDataRole.DisplayRole)
            if not enabled:
                return QtGui.QColor(QtCore.Qt.GlobalColor.gray)
            else:
                return QtGui.QColor(QtCore.Qt.GlobalColor.black)

        if role == QtCore.Qt.ItemDataRole.ToolTipRole:
            if self.problem[str(item.row())] != "":
                return self.problem[str(item.row())]
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            p = re.compile(r"(.*\()(.*)(\))")
            try:
                if p.search(value):
                    c = p.sub(r"\1", value)
                    s = p.sub(r"\2", value)
                    e = p.sub(r"\3", value)

                    if c.strip("(") in ("PortalTo",):
                        ss = getHumanReadableFromId("views", int(s))
                    elif c.strip("(") in (
                        "DroppedOn",
                        "HideObject",
                        "ShowObject",
                        "AllowTake",
                        "DisallowTake",
                    ):
                        ss = getHumanReadableFromId("objects", int(s))
                    else:
                        return value

                    return p.sub(r"\1XXX\3", value).replace("XXX", str(ss))
            except:
                pass

            if item.column() == 6:
                if value:
                    return "True"
                else:
                    return "False"

        # default
        return value

    def flags(self, index):
        flag = QtCore.QAbstractTableModel.flags(self, index)
        flag |= QtCore.Qt.ItemFlag.ItemIsEditable
        return flag

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            # self.emit(QtCore.Signal("dataChanged(QModelIndex,QModelIndex)"), index, index)
            # https://stackoverflow.com/questions/14001592/pyqt-qtableview-doesnt-respond-datachanged-signal
            self.dataChanged.emit(index, index)
            if self._signal_update is not None:
                pri_key = self.index(index.row(), 0)
                _id = self.data(pri_key, QtCore.Qt.ItemDataRole.DisplayRole)
                self._signal_update(index, _id, value)
            return True
        else:
            return False


class ActionList:
    def __init__(self, parent_id, table_view, action_type, media_path):
        self.model = None
        self.current_id = None
        self.table_view = table_view
        self.parent_id = parent_id
        self.action_type = action_type
        self.media_path = media_path

        self.add_del_busy: bool = False

        # Always show vertical scroll bar for action lists
        self.table_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.initializeDatabases()
        self.initializeViews()

    def filterActions(self):
        # REMEMBER to set parent_id in your instance before calling this!
        sql = (
            f"select * from actions where ContextType = '{self.action_type}' "
            f"and ContextId = '{self.parent_id}' order by RowOrder"
        )
        self.model.setQuery(sql)
        if not self.model.lastError().isValid():
            self.connectVALModelToTableView(self.model, self.table_view)
        else:
            log.error(f"Problem in filterActions({self.parent_id}): {self.model.lastError().text()}")
        self.table_view.hideColumn(0)  # id
        self.table_view.hideColumn(1)  # ContextType
        self.table_view.hideColumn(2)  # ContextId
        # self.tableView.hideColumn(3) #Condition
        # self.tableView.hideColumn(4) #Trigger
        # self.tableView.hideColumn(5) #Action
        self.table_view.resizeColumnsToContents()

    def handleActionAdd(self):
        if self.add_del_busy:
            return

        self.add_del_busy = True
        try:
            if self.parent_id is not None:
                # (Id INT, Context TEXT, Condition TEXT, Trigger TEXT, Action TEXT)
                new_id = get_next_value("Id", "actions", default=0)
                new_order = get_next_value("RowOrder", "actions", default=0)

                query = QtSql.QSqlQuery()
                query.prepare(
                    "INSERT INTO actions (Id, ContextType, ContextId, Condition, Trigger, Action, Enabled, RowOrder) "
                    "VALUES (:id, :contexttype, :contextid, :condition, :trigger, :action, :enabled, :roworder)"
                )
                query.bindValue(":id", new_id)
                query.bindValue(":contexttype", self.action_type)
                query.bindValue(":contextid", self.parent_id)
                query.bindValue(":condition", "")
                query.bindValue(":trigger", "")
                query.bindValue(":action", "")
                query.bindValue(":enabled", 1)
                query.bindValue(":roworder", new_order)
                query.exec()
                if query.lastError().isValid():
                    log.error(f"Problem in handleActionAdd(): {query.lastError().text()}")
                self.filterActions()
                self.table_view.scrollToBottom()
        finally:
            self.add_del_busy = False

    def handleActionDel(self):
        if self.add_del_busy:
            return

        self.add_del_busy = True
        try:
            if self.current_id is not None:
                # Make sure first
                ret = QMessageBox.question(
                    None,
                    f"Really Delete Action #{self.current_id}",
                    "Really delete this action?",
                    QtWidgets.QMessageBox.StandardButton.Cancel | QtWidgets.QMessageBox.StandardButton.Ok,
                    QtWidgets.QMessageBox.StandardButton.Cancel,
                )

                if ret == QtWidgets.QMessageBox.StandardButton.Ok:
                    # delete action
                    query1 = QtSql.QSqlQuery()
                    query1.prepare("DELETE FROM actions where Id = :id")
                    query1.bindValue(":id", self.current_id)
                    query1.exec()
                    if query1.lastError().isValid():
                        log.error(f"Problem in handleActionDel(): {query1.lastError().text()}")
                    # clear current_id
                    self.current_id = None
                    # reset actionview
                    if self.parent_id is not None:
                        self.filterActions()
        finally:
            self.add_del_busy = False

    def initializeVALModel(self, model, query):
        model.setQuery(query)
        # (Id INT, Context TEXT, Condition TEXT, Trigger TEXT, Action TEXT, Enabled BOOL, RowOrder INT)
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Id")
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "ContextType")
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, "ContextId")
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, "Condition")
        model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, "Trigger")
        model.setHeaderData(5, QtCore.Qt.Orientation.Horizontal, "Action")
        model.setHeaderData(6, QtCore.Qt.Orientation.Horizontal, "Enabled")
        model.setHeaderData(7, QtCore.Qt.Orientation.Horizontal, "RowOrder")

    def connectVALModelToTableView(self, model, view):
        # Note: The really doesn't do anything because there is no model yet.
        #      Model is set via query and columns hidden here: self.filterActions()
        view.setModel(model)
        view.hideColumn(0)  # id
        view.hideColumn(1)  # ContextType
        view.hideColumn(2)  # ContextId
        # view.hideColumn(3) #Condition
        # view.hideColumn(4) #Trigger
        # view.hideColumn(5) #Action
        # view.hideColumn(6) #Enabled
        view.hideColumn(7)  # RowOrder
        view.resizeColumnsToContents()

    def signalActionUpdate(self, index, record_id, value):
        # http://goo.gl/3afhWi
        # http://goo.gl/7hQVmT

        # Get info needed for doing update
        col = index.column()
        field_name = str(
            self.model.headerData(
                col,
                QtCore.Qt.Orientation.Horizontal,
                QtCore.Qt.ItemDataRole.DisplayRole,
            )
        )

        # Update database
        if field_name in ("Condition", "Trigger", "Action", "Enabled"):
            query = QtSql.QSqlQuery()
            query.prepare("UPDATE actions SET " + field_name + " = :value WHERE Id = :id")
            if type(value) is int:
                query.bindValue(":value", value)
            # todo: temporarily removing escape stuff...I need to see if it's EVER ok to enter html code.
            #  If not, no escape needed!
            # elif re.findall('\"[^\"]+\"', value):
            #     if '<' in value and '>' in value:  # must be html?
            #         query.bindValue(":value", f'{value[0]}{escape(value[1:-1])}{value[-1]}')
            #     else:
            #         query.bindValue(":value", f'{value[0]}{value[1:-1]}{value[-1]}')
            # else:
            #     if '<' in value and '>' in value:  # must be html?
            #         query.bindValue(":value", escape(value))
            #     else:
            #         query.bindValue(":value", value)
            elif re.findall('"[^"]+"', value):
                query.bindValue(":value", f"{value[0]}{value[1:-1]}{value[-1]}")
            else:
                query.bindValue(":value", value)
            query.bindValue(":id", record_id)
            query.exec()
            if query.lastError().isValid():
                log.error(f"Problem in signalActionUpdate() update query failed: {query.lastError().text()}")

        # Refresh Table View after the editor closes
        # Use QTimer.singleShot to defer refresh until after the current event loop
        if self.parent_id is not None:
            QTimer.singleShot(0, self.filterActions)

        mark_db_as_changed()

    def initializeDatabases(self):
        self.model = CustomSqlModel2()
        self.model.initSignal(self.signalActionUpdate)

    def initializeViews(self):
        # setup delegates
        delegate = generic_col_delegates.GenericDelegate()
        delegate.insertColumnDelegate(
            3,
            generic_col_delegates.ActionColumnDelegate("Condition", self.action_type, self.media_path),
        )  # 3
        delegate.insertColumnDelegate(
            4,
            generic_col_delegates.ActionColumnDelegate("Trigger", self.action_type, self.media_path),
        )  # 4
        delegate.insertColumnDelegate(
            5,
            generic_col_delegates.ActionColumnDelegate("Action", self.action_type, self.media_path),
        )  # 5
        delegate.insertColumnDelegate(6, generic_col_delegates.IntegerColumnDelegate(0, 1))  # 6
        # delegate.insertColumnDelegate(6, genericcoldelegates.TFComboColumnDelegate())  # 6
        self.table_view.setItemDelegate(delegate)
