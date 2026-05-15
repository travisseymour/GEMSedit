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

import re

from PySide6 import QtCore, QtGui, QtSql, QtWidgets
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QMessageBox

from gemsedit import log
from gemsedit.database.connection import mark_db_as_changed

# from html import escape
from gemsedit.database.sqltools import get_next_value
import gemsedit.gui.genericcoldelegates as generic_col_delegates


def parse_linked_object_name(object_name: str) -> tuple[int, int] | None:
    """
    Parse an object name to check if it references another object's actions.

    Objects with names ending in _[VIEWID]_[OBJECTID] will use the actions
    from the referenced object instead of having their own actions.

    Args:
        object_name: The name of the object to check

    Returns:
        A tuple of (view_id, object_id) if the name matches the pattern,
        or None if it doesn't match.

    Examples:
        "Doorknob_3_7" -> (3, 7)  # Uses actions from object 7 in view 3
        "Doorknob" -> None  # Normal object
        "Door_handle" -> None  # Underscore but not the pattern
    """
    if not object_name:
        return None

    # Pattern: anything followed by _NUMBER_NUMBER at the end
    pattern = r"^.+_(\d+)_(\d+)$"
    match = re.match(pattern, object_name)

    if match:
        view_id = int(match.group(1))
        object_id = int(match.group(2))
        return (view_id, object_id)

    return None


def get_linked_object_info(view_id: int, object_id: int) -> dict | None:
    """
    Get information about a linked object.

    Args:
        view_id: The ID of the view containing the source object
        object_id: The ID of the source object

    Returns:
        A dict with 'view_name', 'object_name', 'object_id' if found, else None
    """
    # First verify the object exists and belongs to the specified view
    query = QtSql.QSqlQuery()
    query.prepare("SELECT Name, Parent FROM objects WHERE Id = :id")
    query.bindValue(":id", object_id)
    query.exec()

    if not query.isActive() or not query.next():
        return None

    obj_name = query.value(0)
    parent_view_id = query.value(1)

    # Verify the object belongs to the specified view
    if parent_view_id != view_id:
        return None

    # Get the view name
    view_query = QtSql.QSqlQuery()
    view_query.prepare("SELECT Name FROM views WHERE Id = :id")
    view_query.bindValue(":id", view_id)
    view_query.exec()

    if not view_query.isActive() or not view_query.next():
        return None

    view_name = view_query.value(0)

    return {
        "view_id": view_id,
        "view_name": view_name,
        "object_id": object_id,
        "object_name": obj_name,
    }


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


class CopyActionsDialog(QtWidgets.QDialog):
    """Dialog for selecting a source view or object to copy actions from."""

    def __init__(self, action_type: str, current_id: int, parent=None):
        super().__init__(parent)
        self.action_type = action_type
        self.current_id = current_id
        self.selected_id = None

        if action_type == "view":
            self.setWindowTitle("Copy Actions From View")
        else:
            self.setWindowTitle("Copy Actions From Object")

        self.setMinimumSize(400, 300)
        self.setup_ui()
        self.load_items()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        if self.action_type == "view":
            label = QtWidgets.QLabel("Select a view to copy actions from:")
        else:
            label = QtWidgets.QLabel("Select an object to copy actions from:")
        layout.addWidget(label)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree_widget)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.select_button = QtWidgets.QPushButton("Select")
        self.select_button.clicked.connect(self.on_select)
        self.select_button.setEnabled(False)
        button_layout.addWidget(self.select_button)

        layout.addLayout(button_layout)

        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)

    def load_items(self):
        self.tree_widget.clear()

        if self.action_type == "view":
            self._load_views()
        else:
            self._load_objects()

    def _load_views(self):
        query = QtSql.QSqlQuery()
        query.exec("SELECT Id, Name FROM views ORDER BY RowOrder")
        if query.isActive():
            while query.next():
                view_id = query.value(0)
                view_name = query.value(1)
                if view_id != self.current_id:
                    item = QtWidgets.QTreeWidgetItem([f"{view_name} ({view_id})"])
                    item.setData(0, QtCore.Qt.ItemDataRole.UserRole, view_id)
                    item.setData(0, QtCore.Qt.ItemDataRole.UserRole + 1, "view")
                    self.tree_widget.addTopLevelItem(item)

    def _load_objects(self):
        views_query = QtSql.QSqlQuery()
        views_query.exec("SELECT Id, Name FROM views ORDER BY RowOrder")
        if views_query.isActive():
            while views_query.next():
                view_id = views_query.value(0)
                view_name = views_query.value(1)

                view_item = QtWidgets.QTreeWidgetItem([f"{view_name} ({view_id})"])
                view_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, None)
                view_item.setData(0, QtCore.Qt.ItemDataRole.UserRole + 1, "view_header")

                objects_query = QtSql.QSqlQuery()
                objects_query.prepare("SELECT Id, Name FROM objects WHERE Parent = :parent ORDER BY RowOrder")
                objects_query.bindValue(":parent", view_id)
                objects_query.exec()

                has_objects = False
                if objects_query.isActive():
                    while objects_query.next():
                        obj_id = objects_query.value(0)
                        obj_name = objects_query.value(1)
                        if obj_id != self.current_id:
                            has_objects = True
                            obj_item = QtWidgets.QTreeWidgetItem([f"  {obj_name} ({obj_id})"])
                            obj_item.setData(0, QtCore.Qt.ItemDataRole.UserRole, obj_id)
                            obj_item.setData(0, QtCore.Qt.ItemDataRole.UserRole + 1, "object")
                            view_item.addChild(obj_item)

                if has_objects:
                    self.tree_widget.addTopLevelItem(view_item)
                    view_item.setExpanded(True)

    def on_selection_changed(self):
        items = self.tree_widget.selectedItems()
        if items:
            item = items[0]
            item_type = item.data(0, QtCore.Qt.ItemDataRole.UserRole + 1)
            item_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            if self.action_type == "view":
                self.select_button.setEnabled(item_type == "view" and item_id is not None)
            else:
                self.select_button.setEnabled(item_type == "object" and item_id is not None)
        else:
            self.select_button.setEnabled(False)

    def on_item_double_clicked(self, item, column):
        item_type = item.data(0, QtCore.Qt.ItemDataRole.UserRole + 1)
        item_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
        if self.action_type == "view" and item_type == "view" and item_id is not None:
            self.selected_id = item_id
            self.accept()
        elif self.action_type == "object" and item_type == "object" and item_id is not None:
            self.selected_id = item_id
            self.accept()

    def on_select(self):
        items = self.tree_widget.selectedItems()
        if items:
            item = items[0]
            self.selected_id = item.data(0, QtCore.Qt.ItemDataRole.UserRole)
            self.accept()


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
            # Gray text for disabled rows, use palette text color for enabled (dark mode compatible)
            enabled_index = self.index(item.row(), 6)
            enabled = super().data(enabled_index, QtCore.Qt.ItemDataRole.DisplayRole)
            if not enabled:
                return QtGui.QColor(QtCore.Qt.GlobalColor.gray)
            else:
                # Return None to use the default palette text color (works in both light and dark modes)
                return None

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


class LinkedEditEventFilter(QtCore.QObject):
    """Event filter to intercept editing attempts on linked action lists."""

    def __init__(self, action_list: "ActionList", parent=None):
        super().__init__(parent)
        self.action_list = action_list
        self._warned_this_session = False

    def eventFilter(self, obj, event):
        # Intercept double-click which triggers editing
        if event.type() == QtCore.QEvent.Type.MouseButtonDblClick:
            if self.action_list.is_linked():
                if not self._warned_this_session:
                    # Show warning dialog
                    ret = QMessageBox.warning(
                        None,
                        "Editing Linked Actions",
                        "This object's actions are linked from another object.\n\n"
                        "Any changes you make here will affect ALL objects that "
                        "share these linked actions.\n\n"
                        "Do you want to proceed with editing?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if ret == QMessageBox.StandardButton.Yes:
                        self._warned_this_session = True
                        return False  # Allow the event to proceed
                    else:
                        return True  # Block the event
                # Already warned, allow editing
                return False
        return False  # Don't block other events

    def reset_warning(self):
        """Reset the warning flag (call when switching to a different linked object)."""
        self._warned_this_session = False


class ActionList:
    def __init__(self, parent_id, table_view, action_type, media_path):
        self.model = None
        self.current_id = None
        self.table_view = table_view
        self.parent_id = parent_id
        self.action_type = action_type
        self.media_path = media_path

        self.add_del_busy: bool = False

        # Linked object support - when set, shows another object's actions read-only
        self.linked_source: dict | None = None
        self._on_linked_changed_callback = None

        # Event filter to intercept editing on linked actions
        self._linked_edit_filter = LinkedEditEventFilter(self)
        self.table_view.viewport().installEventFilter(self._linked_edit_filter)

        # Always show vertical scroll bar for action lists
        self.table_view.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)

        self.initializeDatabases()
        self.initializeViews()

    def set_linked_mode(self, linked_info: dict | None, callback=None):
        """
        Set linked mode for this action list.

        Args:
            linked_info: Dict with view_id, view_name, object_id, object_name from get_linked_object_info(),
                         or None to disable linked mode.
            callback: Optional callback function(is_linked: bool) to be called when linked state changes.
        """
        # Reset warning when linked source changes (different object or disabling linked mode)
        old_source_id = self.linked_source.get("object_id") if self.linked_source else None
        new_source_id = linked_info.get("object_id") if linked_info else None
        if old_source_id != new_source_id:
            self._linked_edit_filter.reset_warning()

        self.linked_source = linked_info
        self._on_linked_changed_callback = callback

        if self._on_linked_changed_callback:
            self._on_linked_changed_callback(linked_info is not None)

    def is_linked(self) -> bool:
        """Return True if this action list is showing linked actions from another object."""
        return self.linked_source is not None

    def get_linked_description(self) -> str:
        """Return a human-readable description of the linked source."""
        if not self.linked_source:
            return ""
        return (
            f"Actions linked from: {self.linked_source['view_name']}:{self.linked_source['object_name']} "
            f"(View {self.linked_source['view_id']}, Object {self.linked_source['object_id']})"
        )

    def filterActions(self):
        # REMEMBER to set parent_id in your instance before calling this!
        # If linked to another object, show that object's actions instead
        if self.linked_source:
            source_id = self.linked_source["object_id"]
            sql = f"select * from actions where ContextType = 'object' and ContextId = '{source_id}' order by RowOrder"
        else:
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
        self._configureColumnSizing(self.table_view)

    def handleActionAdd(self):
        if self.add_del_busy or self.is_linked():
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
                else:
                    mark_db_as_changed()
                self.filterActions()
                self.table_view.scrollToBottom()
        finally:
            self.add_del_busy = False

    def handleActionDel(self):
        if self.add_del_busy or self.is_linked():
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
                    else:
                        mark_db_as_changed()
                    # clear current_id
                    self.current_id = None
                    # reset actionview
                    if self.parent_id is not None:
                        self.filterActions()
        finally:
            self.add_del_busy = False

    def handleActionCopy(self):
        """Copy actions from another view or object to the current one."""
        if self.add_del_busy or self.is_linked():
            return

        if self.parent_id is None:
            return

        self.add_del_busy = True
        try:
            dialog = CopyActionsDialog(self.action_type, self.parent_id)
            if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
                return

            source_id = dialog.selected_id
            if source_id is None:
                return

            source_query = QtSql.QSqlQuery()
            source_query.prepare(
                "SELECT Condition, Trigger, Action, Enabled FROM actions "
                "WHERE ContextType = :contexttype AND ContextId = :contextid ORDER BY RowOrder"
            )
            source_query.bindValue(":contexttype", self.action_type)
            source_query.bindValue(":contextid", source_id)
            source_query.exec()

            if source_query.lastError().isValid():
                log.error(f"Problem in handleActionCopy() source query: {source_query.lastError().text()}")
                return

            actions_to_copy = []
            if source_query.isActive():
                while source_query.next():
                    actions_to_copy.append(
                        {
                            "condition": source_query.value(0),
                            "trigger": source_query.value(1),
                            "action": source_query.value(2),
                            "enabled": source_query.value(3),
                        }
                    )

            if not actions_to_copy:
                QMessageBox.information(
                    None,
                    "No Actions to Copy",
                    "The selected source has no actions to copy.",
                    QMessageBox.StandardButton.Ok,
                )
                return

            ret = QMessageBox.question(
                None,
                "Confirm Copy Actions",
                f"Copy {len(actions_to_copy)} action(s) to the current {self.action_type}?\n\n"
                "This will add the actions to the existing action list.",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )

            if ret != QtWidgets.QMessageBox.StandardButton.Yes:
                return

            for action_data in actions_to_copy:
                new_id = get_next_value("Id", "actions", default=0)
                new_order = get_next_value("RowOrder", "actions", default=0)

                insert_query = QtSql.QSqlQuery()
                insert_query.prepare(
                    "INSERT INTO actions (Id, ContextType, ContextId, Condition, Trigger, Action, Enabled, RowOrder) "
                    "VALUES (:id, :contexttype, :contextid, :condition, :trigger, :action, :enabled, :roworder)"
                )
                insert_query.bindValue(":id", new_id)
                insert_query.bindValue(":contexttype", self.action_type)
                insert_query.bindValue(":contextid", self.parent_id)
                insert_query.bindValue(":condition", action_data["condition"])
                insert_query.bindValue(":trigger", action_data["trigger"])
                insert_query.bindValue(":action", action_data["action"])
                insert_query.bindValue(":enabled", action_data["enabled"])
                insert_query.bindValue(":roworder", new_order)
                insert_query.exec()

                if insert_query.lastError().isValid():
                    log.error(f"Problem in handleActionCopy() insert: {insert_query.lastError().text()}")

            self.filterActions()
            self.table_view.scrollToBottom()
            mark_db_as_changed()

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
        view.setModel(model)
        view.hideColumn(0)  # id
        view.hideColumn(1)  # ContextType
        view.hideColumn(2)  # ContextId
        view.hideColumn(7)  # RowOrder
        self._configureColumnSizing(view)
        # Move Enabled column to the front of the visible columns
        header = view.horizontalHeader()
        if header.visualIndex(6) != 3:
            header.moveSection(header.visualIndex(6), 3)

    def _configureColumnSizing(self, view):
        header = view.horizontalHeader()
        header.setStretchLastSection(False)
        # Enabled, Condition, Trigger: fit to widest content + padding
        padding = view.fontMetrics().averageCharWidth()
        for col in (6, 3, 4):
            view.resizeColumnToContents(col)
            header.resizeSection(col, header.sectionSize(col) + padding)
        # Action: fill remaining space
        header.setSectionResizeMode(5, QtWidgets.QHeaderView.ResizeMode.Stretch)

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
        delegate.insertColumnDelegate(6, generic_col_delegates.BooleanColumnDelegate())  # 6
        self.table_view.setItemDelegate(delegate)
