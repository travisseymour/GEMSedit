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

from datetime import datetime
import json
import os
import re

from PySide6 import QtCore, QtGui, QtSql, QtWidgets
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMessageBox

import gemsedit
from gemsedit import dialog_font, log
from gemsedit.database.connection import mark_db_as_changed

# Todo: when entering actions, sometimes the object list selection goes somewhere else.
from gemsedit.database.sqltools import get_next_value
from gemsedit.gui import action_list, object_select_widget as objselect
from gemsedit.gui.action_list import get_linked_object_info, parse_linked_object_name
import gemsedit.gui.objects_window as win
from gemsedit.gui.tagged_model import TaggedSqlModel, build_tag_color_map
from gemsedit.utils.polygon_utils import json_to_points, points_to_bounding_rect, polygons_overlap


class ClickEventFilter(QtCore.QObject):
    """Event filter that calls a callback when a widget is clicked."""

    def __init__(self, callback, parent=None):
        super().__init__(parent)
        self.callback = callback

    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == QtCore.Qt.MouseButton.LeftButton:
                self.callback()
                return True
        return super().eventFilter(obj, event)


class CopyObjectsDialog(QtWidgets.QDialog):
    """Dialog for selecting a source view to copy all objects from."""

    def __init__(self, current_view_id: int, parent=None):
        super().__init__(parent)
        self.current_view_id = current_view_id
        self.selected_view_id = None

        self.setWindowTitle("Copy Objects From View")
        self.setMinimumSize(400, 300)
        self.setup_ui()
        self.load_views()

    def setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        label = QtWidgets.QLabel("Select a view to copy all objects from:")
        layout.addWidget(label)

        self.list_widget = QtWidgets.QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.list_widget)

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

        self.list_widget.itemSelectionChanged.connect(self.on_selection_changed)

    def load_views(self):
        self.list_widget.clear()

        query = QtSql.QSqlQuery()
        query.exec("SELECT Id, Name FROM views ORDER BY RowOrder")
        if query.isActive():
            while query.next():
                view_id = query.value(0)
                view_name = query.value(1)
                if view_id != self.current_view_id:
                    item = QtWidgets.QListWidgetItem(f"{view_name}")
                    item.setData(QtCore.Qt.ItemDataRole.UserRole, view_id)
                    self.list_widget.addItem(item)

    def on_selection_changed(self):
        items = self.list_widget.selectedItems()
        self.select_button.setEnabled(len(items) > 0)

    def on_item_double_clicked(self, item):
        self.selected_view_id = item.data(QtCore.Qt.ItemDataRole.UserRole)
        self.accept()

    def on_select(self):
        items = self.list_widget.selectedItems()
        if items:
            self.selected_view_id = items[0].data(QtCore.Qt.ItemDataRole.UserRole)
            self.accept()


class Objects:
    def __init__(self, parentid, mediapath, parent_win):
        self.parentid = parentid
        self.mediapath = mediapath
        self.parent_win = parent_win
        self.parentname = None
        self.parent_fg_pic = None

        self.model = None
        self.currentrow = None
        self.basename = "Object"
        self.basetablename = "objects"

        self.MainWindow = QtWidgets.QDialog()
        self.ui = win.Ui_ObjectsWindow()
        self.ui.setupUi(self.MainWindow)
        gemsedit.scale_widget_fonts(self.MainWindow)
        self.selectionmodel = None
        self.objbox = self.create_box(self.ui.objectLocPic_label, 0, 0, 0, 0, "yellow", "ObjectBox")

        self.actionlist = None

        # Track broken link references (pattern matched but source object not found)
        self.broken_link_ref: tuple[int, int] | None = None

        self.getParentInfo()
        self.initializeDatabases()
        self.initializeViews()
        self.connectSlots()

        self.center()

    def center(self):
        geometry = gemsedit.SETTINGS.value("objects_window_geometry")
        if geometry is not None:
            self.MainWindow.restoreGeometry(geometry)
        else:
            qr = self.MainWindow.frameGeometry()
            cp = QGuiApplication.primaryScreen().availableGeometry().center()
            qr.moveCenter(cp)
            self.MainWindow.move(qr.topLeft())

    def closeTheWindow(self):
        gemsedit.SETTINGS.setValue("objects_window_geometry", self.MainWindow.saveGeometry())
        self.parent_win.show()
        self.MainWindow.close()

    def connectSlots(self):
        self.ui.object_tableView.doubleClicked.connect(self.handleBaseDoubleClick)
        self.ui.object_tableView.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.object_tableView.customContextMenuRequested.connect(self._object_tag_context_menu)
        self.ui.objectAdd_toolButton.pressed.connect(self.handleBaseAdd)
        self.ui.objectDel_toolButton.pressed.connect(self.handleBaseDel)
        self.ui.objectCopy_toolButton.pressed.connect(self.handleObjectsCopy)
        self.ui.objectUp_toolButton.pressed.connect(self.handleObjectMoveUp)
        self.ui.objectDown_toolButton.pressed.connect(self.handleObjectMoveDown)
        self.ui.OAL_tableView.clicked.connect(self.handleActionClick)
        self.ui.actionAdd_toolButton.pressed.connect(self.actionlist.handleActionAdd)
        self.ui.actionDel_toolButton.pressed.connect(self.actionlist.handleActionDel)
        self.ui.actionCopy_toolButton.pressed.connect(self.actionlist.handleActionCopy)
        self.ui.actionDuplicate_toolButton.pressed.connect(self.actionlist.handleActionDuplicate)
        self.ui.actionUp_toolButton.pressed.connect(self.actionlist.handleActionMoveUp)
        self.ui.actionDown_toolButton.pressed.connect(self.actionlist.handleActionMoveDown)
        self.ui.takeable_checkBox.toggled.connect(self.updateTakeable)
        self.ui.draggable_checkBox.toggled.connect(self.updateDraggable)
        self.ui.visible_checkBox.toggled.connect(self.updateVisible)
        self.ui.delSelect_toolButton.pressed.connect(lambda: self.handlePicEdit(mode="delete"))
        self.ui.drawSelect_toolButton.pressed.connect(lambda: self.handlePicEdit(mode="select"))

        # Install event filter for picture label click
        self.pic_click_filter = ClickEventFilter(lambda: self.handlePicEdit(mode="viewonly"))
        self.ui.objectLocPic_label.installEventFilter(self.pic_click_filter)

        self.ui.closeButton.pressed.connect(self.closeTheWindow)

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def strIsPattern(self, s, p):
        # True if pattern found
        m = re.search(p, s)
        # set to None if p doesn't match ALL chars in s
        if m and not len(m.group()) == len(s):
            m = None
        return m

    def handleActionClick(self, index):
        id = index.model().record(index.row()).value("Id")
        self.actionlist.current_id = id

    def reinstateViewSelection(self, row=-1):
        # http://qt-project.org/doc/qt-4.8/model-view-programming.html#using-a-selection-model
        if row >= 0:
            curr_row = row
        else:
            curr_row = self.currentrow
        if curr_row is not None and curr_row >= 0:
            currrowindex = self.model.index(curr_row, 0, QtCore.QModelIndex())
            sel = QtCore.QItemSelection(currrowindex, currrowindex)
            self.selectionmodel.select(sel, QtCore.QItemSelectionModel.SelectionFlag.Select)
            self.ui.object_tableView.selectRow(curr_row)

    def handlePicEdit(self, mode):
        if mode == "delete":
            if self.parentid is None or self.currentrow is None:
                return
            id = self.model.record(self.currentrow).value("Id")
            query = QtSql.QSqlQuery()
            sql = f"UPDATE {self.basetablename} SET Points = :points WHERE Id = :id"
            query.prepare(sql)
            query.bindValue(":points", "[]")  # Empty polygon
            query.bindValue(":id", id)
            query.exec()
            if query.lastError().isValid():
                log.error(f"Problem in handlePicEdit() delete query: {query.lastError().text()}")
            sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
            self.model.setQuery(sql)
            self.loadPicFields()
            self.reinstateViewSelection()
            mark_db_as_changed()
        elif mode == "select":
            if self.parentid is None or self.currentrow is None:
                return
            self.MainWindow.hide()
            id = self.model.record(self.currentrow).value("Id")
            obj_selector = objselect.ObjectSelect(
                current_view=self.parentid,
                current_obj=id,
                allow_selection=True,
                media_path=self.mediapath,
            )
            obj_selector.showMaximized()
            obj_selector.exec()
            self.MainWindow.show()
            if obj_selector._result:
                # Result is now a list of polygon points
                points = obj_selector._result
                points_json = json.dumps(points)
                query = QtSql.QSqlQuery()
                sql = f"UPDATE {self.basetablename} SET Points = :points WHERE Id = :id"
                query.prepare(sql)
                query.bindValue(":points", points_json)
                query.bindValue(":id", id)
                query.exec()
                if query.lastError().isValid():
                    log.error(f"Problem in handlePicEdit() update query: {query.lastError().text()}")
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)
                self.loadPicFields()
                self.reinstateViewSelection()
                mark_db_as_changed()
        elif mode == "viewonly":
            self.MainWindow.hide()
            id = self.model.record(self.currentrow).value("Id")
            obj_selector = objselect.ObjectSelect(
                current_view=self.parentid,
                current_obj=id,
                allow_selection=False,
                view_pic="Foreground",
                media_path=self.mediapath,
            )
            obj_selector.showMaximized()
            obj_selector.exec()
            self.MainWindow.show()

    def create_box(self, targetobject, left, top, width, height, colorname, name="Box"):
        colordict = {
            "red": "rgb(255, 0, 0)",
            "green": "rgb(0, 255, 0)",
            "blue": "rgb(0, 0, 255)",
            "yellow": "rgb(255, 255, 0)",
        }
        select_box = QtWidgets.QFrame(targetobject)
        select_box.setEnabled(True)
        select_box.setGeometry(QtCore.QRect(left, top, width, height))
        select_box.setStyleSheet(f"color: {colordict[str(colorname)]};")
        select_box.setFrameShape(QtWidgets.QFrame.Shape.Box)
        select_box.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        select_box.setLineWidth(3)
        select_box.setObjectName(str(name))
        return select_box

    def clearPicFields(self):
        self.ui.objectLocPic_label.clear()  # .setPixmap(None)
        self.ui.objectPic_label.clear()  # .setPixmap(None)
        self.objbox.setGeometry(0, 0, 0, 0)

    def loadPicFields(self):
        if self.currentrow is None or self.model.rowCount() == 0:
            self.clearPicFields()
            return

        # get object info - now using Points column
        id = self.model.record(self.currentrow).value("Id")
        points_json = self.model.record(self.currentrow).value("Points") or "[]"
        points = json_to_points(points_json)

        # Calculate bounding rect from polygon for display purposes
        left, top, width, height = points_to_bounding_rect(points)

        # show big overview image with polygon overlay
        if os.path.exists(self.parent_fg_pic):
            fg_pixmap = QtGui.QPixmap(self.parent_fg_pic)

            # Create a copy to draw polygon on
            if points:
                display_pixmap = fg_pixmap.copy()
                painter = QtGui.QPainter(display_pixmap)
                painter.setPen(QtGui.QPen(QtGui.QColor("yellow"), 3))
                polygon = QtGui.QPolygon([QtCore.QPoint(p[0], p[1]) for p in points])
                painter.drawPolygon(polygon)
                painter.end()
                self.ui.objectLocPic_label.setPixmap(display_pixmap)
            else:
                self.ui.objectLocPic_label.setPixmap(fg_pixmap)

            self.ui.objectLocPic_label.setScaledContents(True)

            # Update objbox to show bounding rect (for backward compatibility)
            label_width = self.ui.objectLocPic_label.width()
            label_height = self.ui.objectLocPic_label.height()
            if width > 0 and height > 0:
                xl = float(left) / float(fg_pixmap.width())
                xt = float(top) / float(fg_pixmap.height())
                xw = float(width) / float(fg_pixmap.width())
                xh = float(height) / float(fg_pixmap.height())
                self.objbox.setGeometry(
                    int(xl * label_width),
                    int(xt * label_height),
                    int(xw * label_width),
                    int(xh * label_height),
                )
            else:
                self.objbox.setGeometry(0, 0, 0, 0)
        else:
            self.ui.objectLocPic_label.clear()

        # show object image (polygon-clipped thumbnail)
        if os.path.exists(self.parent_fg_pic) and width > 0 and height > 0:
            obj_pixmap = self._create_polygon_thumbnail(self.parent_fg_pic, points)
            self.ui.objectPic_label.clear()
            self.ui.objectPic_label.setPixmap(obj_pixmap)
            self.ui.objectPic_label.setScaledContents(True)
        else:
            self.ui.objectPic_label.clear()

    def _create_polygon_thumbnail(self, image_path: str, points: list) -> QtGui.QPixmap:
        """Create a thumbnail cropped and masked to the polygon shape."""
        source = QtGui.QPixmap(image_path)
        if not points or source.isNull():
            return QtGui.QPixmap()

        left, top, width, height = points_to_bounding_rect(points)
        if width <= 0 or height <= 0:
            return QtGui.QPixmap()

        # Create result pixmap with transparency
        result = QtGui.QPixmap(width, height)
        result.fill(QtCore.Qt.GlobalColor.transparent)

        # Create painter path for clipping
        path = QtGui.QPainterPath()
        # Translate points to local coordinates
        local_points = [[p[0] - left, p[1] - top] for p in points]
        if local_points:
            path.moveTo(local_points[0][0], local_points[0][1])
            for p in local_points[1:]:
                path.lineTo(p[0], p[1])
            path.closeSubpath()

        painter = QtGui.QPainter(result)
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, source, left, top, width, height)
        painter.end()

        return result

    # Note: connected to listview *after* list is filled from db
    def handleSelectionChange(self, selected, deselected):
        try:
            # get some required info
            row = QtCore.QItemSelection(selected).indexes()[0].row()
            obj_id = QtCore.QItemSelection(selected).indexes()[0].model().record(row).value("Id")
            obj_name = QtCore.QItemSelection(selected).indexes()[0].model().record(row).value("Name")
            visible = QtCore.QItemSelection(selected).indexes()[0].model().record(row).value("Visible")
            takeable = QtCore.QItemSelection(selected).indexes()[0].model().record(row).value("Takeable")
            draggable = QtCore.QItemSelection(selected).indexes()[0].model().record(row).value("Draggable")

            # disable checkbox handerls prior to updating checkboxes or you'll get circular mess
            self.ui.takeable_checkBox.toggled.disconnect()
            self.ui.draggable_checkBox.toggled.disconnect()
            self.ui.visible_checkBox.toggled.disconnect()

            # update checkboxes
            self.ui.visible_checkBox.setChecked(visible)
            self.ui.takeable_checkBox.setChecked(takeable)
            self.ui.draggable_checkBox.setChecked(draggable)

            # reinstate checkbox handlers
            self.ui.takeable_checkBox.toggled.connect(self.updateTakeable)
            self.ui.draggable_checkBox.toggled.connect(self.updateDraggable)
            self.ui.visible_checkBox.toggled.connect(self.updateVisible)

            # reflect change in ui
            self.currentrow = row
            self.actionlist.parent_id = obj_id

            # Check if this object has a linked action name pattern
            linked_ref = parse_linked_object_name(obj_name)
            if linked_ref:
                view_id, source_obj_id = linked_ref
                linked_info = get_linked_object_info(view_id, source_obj_id)
                if linked_info:
                    self.broken_link_ref = None
                    self.actionlist.set_linked_mode(linked_info, self._on_linked_mode_changed)
                else:
                    # Pattern matched but object not found - this is a broken link
                    self.broken_link_ref = (view_id, source_obj_id)
                    self.actionlist.set_linked_mode(None, self._on_linked_mode_changed)
                    log.warning(f"Object '{obj_name}' references non-existent object {source_obj_id} in view {view_id}")
            else:
                self.broken_link_ref = None
                self.actionlist.set_linked_mode(None, self._on_linked_mode_changed)

            self.actionlist.filterActions()
            self._update_linked_status_display()

            self.loadPicFields()
        except Exception as e:
            log.error(f"Problem in handleSelectionChange({selected}, {deselected}): {e}")

    def _on_linked_mode_changed(self, is_linked: bool):
        """Callback when linked mode changes - enable/disable action buttons."""
        # Disable buttons if linked OR if there's a broken link
        should_disable = is_linked or self.broken_link_ref is not None
        self.ui.actionAdd_toolButton.setEnabled(not should_disable)
        self.ui.actionDel_toolButton.setEnabled(not should_disable)
        self.ui.actionCopy_toolButton.setEnabled(not should_disable)
        self.ui.actionDuplicate_toolButton.setEnabled(not should_disable)

    def _update_linked_status_display(self):
        """Update the UI to show linked status information."""
        if self.actionlist.is_linked():
            desc = self.actionlist.get_linked_description()
            self.ui.label_3.setText("Object Action List (LINKED)")
            self.ui.label_3.setToolTip(desc)
            # Orange background for linked status
            self.ui.label_3.setStyleSheet("background-color: rgb(255, 200, 100)")
        elif self.broken_link_ref is not None:
            view_id, obj_id = self.broken_link_ref
            self.ui.label_3.setText("Object Action List (BROKEN LINK)")
            self.ui.label_3.setToolTip(
                f"Broken link: Object {obj_id} in View {view_id} not found.\n"
                "Rename this object to fix or remove the link."
            )
            # Red background for broken link
            self.ui.label_3.setStyleSheet("background-color: rgb(255, 150, 150)")
            # Also disable buttons for broken links
            self.ui.actionAdd_toolButton.setEnabled(False)
            self.ui.actionDel_toolButton.setEnabled(False)
            self.ui.actionCopy_toolButton.setEnabled(False)
            self.ui.actionDuplicate_toolButton.setEnabled(False)
        else:
            self.ui.label_3.setText("Object Action List")
            self.ui.label_3.setToolTip("")
            self.ui.label_3.setStyleSheet("background-color: rgb(102, 204, 255)")

    def handleBaseDoubleClick(self, index):
        # id =  self.getIdFromClick(index)
        # name = self.getNameFromClick(index)
        id = index.model().record(index.row()).value("Id")
        name = index.model().record(index.row()).value("Name")
        self.editBaseName(id, name)

    def handleBaseAdd(self):
        bn = self.basename.title()
        newid = get_next_value(column_name="Id", table_name=self.basename.lower() + "s", default=0)
        neworder = get_next_value(column_name="RowOrder", table_name=self.basename.lower() + "s", default=0)
        newname = f"New{bn}{newid}"

        # get list of old names
        namelist = []
        query = QtSql.QSqlQuery()
        query.exec(f"select Name from {self.basetablename} where Parent = {self.parentid}")
        if query.isActive():
            while query.next():
                namelist.append(query.value(0))

        text = "???"
        newname = text
        ok = True
        while ok is True and ((not self.strIsPattern(newname, r"\w*")) or (newname in namelist)):
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                "Adding New " + bn,
                "Enter an " + bn + " name (alpha numeric only, no spaces):",
            )
            newname = str(text)
            if ok:
                if not self.strIsPattern(newname, r"\w*"):  # newname.isalpha():
                    _ = QMessageBox.information(
                        self.parent_win,
                        "Bad Object Name",
                        "Object Name Error: Name must consist of only characters from this "
                        "set: [a-zA-Z0-9_]. Please choose another name.",
                        QMessageBox.StandardButton.Ok,
                    )
                elif newname in namelist:
                    _ = QMessageBox.information(
                        self.parent_win,
                        "Bad Object Name",
                        f'Object Name Error: An object called "{newname}" already exists in '
                        f'"{self.parentname}". Please choose another name.',
                        QMessageBox.StandardButton.Ok,
                    )

        if ok:
            newname = str(text)
            query = QtSql.QSqlQuery()
            query.prepare(
                "INSERT INTO "
                "objects (Id, Parent, Name, Points, Visible, Takeable, Draggable, Tag, RowOrder) "
                "VALUES "
                "(:id, :parent, :name, :points, :visible, :takeable, :draggable, :tag, :roworder)"
            )
            query.bindValue(":id", newid)
            query.bindValue(":parent", self.parentid)
            query.bindValue(":name", newname)
            query.bindValue(":points", "[]")  # Empty polygon initially
            query.bindValue(":visible", 1)
            query.bindValue(":takeable", 0)
            query.bindValue(":draggable", 0)
            query.bindValue(":tag", "")
            query.bindValue(":roworder", neworder)
            query.exec()
            self.currentrow = None
            if query.lastError().isValid():
                log.error(f"Problem in handleBaseAdd(): {query.lastError().text()}")
            else:
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)
                if self.model.rowCount() > 0:
                    self.currentrow = self.model.rowCount() - 1
                    # self.ui.object_tableView.selectRow(self.currentrow)
                    # self.ui.object_tableView.scrollToBottom()
                    self.reinstateViewSelection()
                    id = self.model.record(self.currentrow).value("Id")
                    self.actionlist.parent_id = id
                else:
                    self.actionlist.parent_id = None
                self.actionlist.filterActions()
                self.loadPicFields()
            mark_db_as_changed()

    def handleBaseDel(self):
        bn = self.basename.title()
        if self.currentrow is not None:
            try:
                id = self.model.record(self.currentrow).value("Id")
                name = self.model.record(self.currentrow).value("Name")
                assert name is not None
            except:
                return
            # Make sure first
            ret = QMessageBox.question(
                self.MainWindow,
                f"Delete {bn} {name}",
                f"Really delete {name} and all of it's associated actions?",
                QtWidgets.QMessageBox.StandardButton.Cancel | QtWidgets.QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Cancel,
            )

            if ret == QtWidgets.QMessageBox.StandardButton.Ok:
                # delete base
                query1 = QtSql.QSqlQuery()
                query1.prepare("DELETE FROM " + self.basetablename + " where Id = :id")
                query1.bindValue(":id", id)
                query1.exec()
                if query1.lastError().isValid():
                    log.error(f"Problem in handleBaseDel(): {query1.lastError().text()}")
                else:
                    # delete associated actions for base
                    query2 = QtSql.QSqlQuery()
                    query2.prepare("DELETE FROM actions where ContextType = :actiontype and ContextId = :id")
                    query2.bindValue(":actiontype", self.basename.lower())
                    query2.bindValue(":id", id)
                    query2.exec()
                    if query2.lastError().isValid():
                        log.error(f"Problem in handleBaseDel(): {query1.lastError().text()}")
                if not query1.lastError().isValid():
                    sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                    self.model.setQuery(sql)
                    if self.model.rowCount() > 0:
                        self.currentrow = self.model.rowCount() - 1
                        # self.ui.object_tableView.selectRow(self.currentrow)
                        # self.ui.object_tableView.scrollToBottom()
                        self.reinstateViewSelection(self.model.rowCount() - 1)
                        id = self.model.record(self.currentrow).value("Id")
                        self.actionlist.parent_id = id

                    else:
                        self.actionlist.parent_id = None
                    self.actionlist.filterActions()
                    self.loadPicFields()

                mark_db_as_changed()

    def handleObjectsCopy(self):
        """Copy all objects and their actions from another view to this view."""
        if self.parentid is None:
            return

        dialog = CopyObjectsDialog(self.parentid, self.MainWindow)
        if dialog.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        source_view_id = dialog.selected_view_id
        if source_view_id is None:
            return

        # Get all objects from the source view
        source_query = QtSql.QSqlQuery()
        source_query.prepare(
            "SELECT Id, Name, Points, Visible, Takeable, Draggable, Tag "
            "FROM objects WHERE Parent = :parent ORDER BY RowOrder"
        )
        source_query.bindValue(":parent", source_view_id)
        source_query.exec()

        if source_query.lastError().isValid():
            log.error(f"Problem in handleObjectsCopy() source query: {source_query.lastError().text()}")
            return

        objects_to_copy = []
        if source_query.isActive():
            while source_query.next():
                objects_to_copy.append(
                    {
                        "id": source_query.value(0),
                        "name": source_query.value(1),
                        "points": source_query.value(2) or "[]",
                        "visible": source_query.value(3),
                        "takeable": source_query.value(4),
                        "draggable": source_query.value(5),
                        "tag": source_query.value(6) or "",
                    }
                )

        if not objects_to_copy:
            QMessageBox.information(
                self.MainWindow,
                "No Objects to Copy",
                "The selected view has no objects to copy.",
                QMessageBox.StandardButton.Ok,
            )
            return

        # Get existing object names in this view to check for conflicts
        existing_names = set()
        name_query = QtSql.QSqlQuery()
        name_query.prepare("SELECT Name FROM objects WHERE Parent = :parent")
        name_query.bindValue(":parent", self.parentid)
        name_query.exec()
        if name_query.isActive():
            while name_query.next():
                existing_names.add(name_query.value(0))

        # Check if any names conflict
        has_conflicts = any(obj["name"] in existing_names for obj in objects_to_copy)

        # Generate time suffix if there are conflicts
        time_suffix = ""
        if has_conflicts:
            time_suffix = datetime.now().strftime("%H%M")

        # Count how many actions will be copied
        total_actions = 0
        for obj in objects_to_copy:
            action_count_query = QtSql.QSqlQuery()
            action_count_query.prepare("SELECT COUNT(*) FROM actions WHERE ContextType = 'object' AND ContextId = :id")
            action_count_query.bindValue(":id", obj["id"])
            action_count_query.exec()
            if action_count_query.isActive() and action_count_query.next():
                total_actions += action_count_query.value(0)

        # Build confirmation message
        suffix_note = ""
        if time_suffix:
            suffix_note = f"\n\nNote: Object names will have '{time_suffix}' appended to avoid conflicts."

        ret = QMessageBox.question(
            self.MainWindow,
            "Confirm Copy Objects",
            f"Copy {len(objects_to_copy)} object(s) and {total_actions} action(s) to this view?{suffix_note}",
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        if ret != QtWidgets.QMessageBox.StandardButton.Yes:
            return

        # Copy each object and its actions
        for obj in objects_to_copy:
            new_obj_id = get_next_value("Id", "objects", default=0)
            new_order = get_next_value("RowOrder", "objects", default=0)

            # Apply time suffix if needed
            new_name = obj["name"]
            if time_suffix:
                new_name = f"{obj['name']}_{time_suffix}"

            # Insert the object
            insert_obj_query = QtSql.QSqlQuery()
            insert_obj_query.prepare(
                "INSERT INTO objects (Id, Parent, Name, Points, Visible, Takeable, Draggable, Tag, RowOrder) "
                "VALUES (:id, :parent, :name, :points, :visible, :takeable, :draggable, :tag, :roworder)"
            )
            insert_obj_query.bindValue(":id", new_obj_id)
            insert_obj_query.bindValue(":parent", self.parentid)
            insert_obj_query.bindValue(":name", new_name)
            insert_obj_query.bindValue(":points", obj["points"])
            insert_obj_query.bindValue(":visible", obj["visible"])
            insert_obj_query.bindValue(":takeable", obj["takeable"])
            insert_obj_query.bindValue(":draggable", obj["draggable"])
            insert_obj_query.bindValue(":tag", obj.get("tag", ""))
            insert_obj_query.bindValue(":roworder", new_order)
            insert_obj_query.exec()

            if insert_obj_query.lastError().isValid():
                log.error(f"Problem in handleObjectsCopy() insert object: {insert_obj_query.lastError().text()}")
                continue

            # Copy actions for this object
            actions_query = QtSql.QSqlQuery()
            actions_query.prepare(
                "SELECT Condition, Trigger, Action, Enabled FROM actions "
                "WHERE ContextType = 'object' AND ContextId = :id ORDER BY RowOrder"
            )
            actions_query.bindValue(":id", obj["id"])
            actions_query.exec()

            if actions_query.isActive():
                while actions_query.next():
                    new_action_id = get_next_value("Id", "actions", default=0)
                    new_action_order = get_next_value("RowOrder", "actions", default=0)

                    insert_action_query = QtSql.QSqlQuery()
                    insert_action_query.prepare(
                        "INSERT INTO actions (Id, ContextType, ContextId, Condition, Trigger, Action, Enabled, RowOrder) "
                        "VALUES (:id, :contexttype, :contextid, :condition, :trigger, :action, :enabled, :roworder)"
                    )
                    insert_action_query.bindValue(":id", new_action_id)
                    insert_action_query.bindValue(":contexttype", "object")
                    insert_action_query.bindValue(":contextid", new_obj_id)
                    insert_action_query.bindValue(":condition", actions_query.value(0))
                    insert_action_query.bindValue(":trigger", actions_query.value(1))
                    insert_action_query.bindValue(":action", actions_query.value(2))
                    insert_action_query.bindValue(":enabled", actions_query.value(3))
                    insert_action_query.bindValue(":roworder", new_action_order)
                    insert_action_query.exec()

                    if insert_action_query.lastError().isValid():
                        log.error(
                            f"Problem in handleObjectsCopy() insert action: {insert_action_query.lastError().text()}"
                        )

        # Refresh the object list
        sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
        self.model.setQuery(sql)
        if self.model.rowCount() > 0:
            self.currentrow = self.model.rowCount() - 1
            self.reinstateViewSelection(self.model.rowCount() - 1)
            obj_id = self.model.record(self.currentrow).value("Id")
            self.actionlist.parent_id = obj_id
            self.actionlist.filterActions()
            self.loadPicFields()

        mark_db_as_changed()

    def handleObjectMoveUp(self):
        if self.currentrow is None:
            return
        _id = self.model.record(self.currentrow).value("Id")
        query = QtSql.QSqlQuery()
        query.prepare("SELECT RowOrder FROM objects WHERE Id = :id")
        query.bindValue(":id", _id)
        query.exec()
        if not query.isActive() or not query.next():
            return
        current_row_order = query.value(0)

        query2 = QtSql.QSqlQuery()
        query2.prepare(
            "SELECT Id, RowOrder FROM objects "
            "WHERE Parent = :parent AND RowOrder < :roworder "
            "ORDER BY RowOrder DESC LIMIT 1"
        )
        query2.bindValue(":parent", self.parentid)
        query2.bindValue(":roworder", current_row_order)
        query2.exec()
        if not query2.isActive() or not query2.next():
            return  # already at top

        swap_id = query2.value(0)
        swap_row_order = query2.value(1)

        update1 = QtSql.QSqlQuery()
        update1.prepare("UPDATE objects SET RowOrder = :roworder WHERE Id = :id")
        update1.bindValue(":roworder", swap_row_order)
        update1.bindValue(":id", _id)
        update1.exec()

        update2 = QtSql.QSqlQuery()
        update2.prepare("UPDATE objects SET RowOrder = :roworder WHERE Id = :id")
        update2.bindValue(":roworder", current_row_order)
        update2.bindValue(":id", swap_id)
        update2.exec()

        if update1.lastError().isValid() or update2.lastError().isValid():
            log.error("Problem in handleObjectMoveUp(): swap failed")
            return

        mark_db_as_changed()
        sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
        self.model.setQuery(sql)
        self._select_object_by_id(_id)

    def handleObjectMoveDown(self):
        if self.currentrow is None:
            return
        _id = self.model.record(self.currentrow).value("Id")
        query = QtSql.QSqlQuery()
        query.prepare("SELECT RowOrder FROM objects WHERE Id = :id")
        query.bindValue(":id", _id)
        query.exec()
        if not query.isActive() or not query.next():
            return
        current_row_order = query.value(0)

        query2 = QtSql.QSqlQuery()
        query2.prepare(
            "SELECT Id, RowOrder FROM objects "
            "WHERE Parent = :parent AND RowOrder > :roworder "
            "ORDER BY RowOrder ASC LIMIT 1"
        )
        query2.bindValue(":parent", self.parentid)
        query2.bindValue(":roworder", current_row_order)
        query2.exec()
        if not query2.isActive() or not query2.next():
            return  # already at bottom

        swap_id = query2.value(0)
        swap_row_order = query2.value(1)

        update1 = QtSql.QSqlQuery()
        update1.prepare("UPDATE objects SET RowOrder = :roworder WHERE Id = :id")
        update1.bindValue(":roworder", swap_row_order)
        update1.bindValue(":id", _id)
        update1.exec()

        update2 = QtSql.QSqlQuery()
        update2.prepare("UPDATE objects SET RowOrder = :roworder WHERE Id = :id")
        update2.bindValue(":roworder", current_row_order)
        update2.bindValue(":id", swap_id)
        update2.exec()

        if update1.lastError().isValid() or update2.lastError().isValid():
            log.error("Problem in handleObjectMoveDown(): swap failed")
            return

        mark_db_as_changed()
        sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
        self.model.setQuery(sql)
        self._select_object_by_id(_id)

    def _select_object_by_id(self, obj_id):
        for row in range(self.model.rowCount()):
            if self.model.record(row).value("Id") == obj_id:
                self.currentrow = row
                self.ui.object_tableView.selectRow(row)
                return

    def editBaseName(self, id, name):
        bn = self.basename.title()
        # get list of old names in this view only
        namelist = []
        query = QtSql.QSqlQuery()
        query.prepare("SELECT Name FROM " + self.basetablename + " WHERE Parent = :parent")
        query.bindValue(":parent", self.parentid)
        query.exec()
        if query.isActive():
            while query.next():
                namelist.append(query.value(0))
        if name in namelist:
            namelist.remove(name)
        # get the name
        text = "???"
        newname = text
        ok = True

        while ok is True and ((not self.strIsPattern(newname, r"\w*")) or (newname in namelist)):
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                f"Change {bn} Name",
                f"Enter an {bn.lower()} name (alpha numeric only, no spaces):",
                text=name,
            )
            newname = str(text)
            if ok:
                if not self.strIsPattern(newname, r"\w*"):
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setText(
                        "Object Name Error: Name must consist of only characters from this set: "
                        "[a-zA-Z0-9_]. Please choose another name."
                    )
                    msgbox.setFont(dialog_font)
                    msgbox.exec()
                elif newname in namelist:
                    msgbox = QtWidgets.QMessageBox()
                    msgbox.setText(
                        f'Object Name Error: An object called "{newname}" already exists in "{self.parentname}". '
                        f"Please choose another name."
                    )
                    msgbox.setFont(dialog_font)
                    msgbox.exec()
        if ok:
            # change name if it's actually different
            if newname != name:
                # Check if new name creates a valid link
                linked_ref = parse_linked_object_name(newname)
                if linked_ref:
                    view_id, source_obj_id = linked_ref
                    linked_info = get_linked_object_info(view_id, source_obj_id)
                    if linked_info:
                        # Check if this object has existing actions that will be hidden
                        action_count_query = QtSql.QSqlQuery()
                        action_count_query.prepare(
                            "SELECT COUNT(*) FROM actions WHERE ContextType = 'object' AND ContextId = :id"
                        )
                        action_count_query.bindValue(":id", id)
                        action_count_query.exec()
                        existing_action_count = 0
                        if action_count_query.isActive() and action_count_query.next():
                            existing_action_count = action_count_query.value(0)

                        if existing_action_count > 0:
                            # Warn user about existing actions being deleted
                            ret = QMessageBox.warning(
                                self.MainWindow,
                                "Link Will Delete Existing Actions",
                                f"This object currently has {existing_action_count} action(s).\n\n"
                                f"Creating a link to '{linked_info['object_name']}' in view "
                                f"'{linked_info['view_name']}' will DELETE these existing actions.\n\n"
                                "Do you want to proceed?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No,
                            )
                            if ret != QMessageBox.StandardButton.Yes:
                                return  # User cancelled, don't rename

                            # Delete existing actions
                            delete_query = QtSql.QSqlQuery()
                            delete_query.prepare("DELETE FROM actions WHERE ContextType = 'object' AND ContextId = :id")
                            delete_query.bindValue(":id", id)
                            delete_query.exec()
                            if delete_query.lastError().isValid():
                                log.error(f"Problem deleting actions before linking: {delete_query.lastError().text()}")

                query = QtSql.QSqlQuery()
                query.prepare("UPDATE " + self.basetablename + " SET Name = :name WHERE Id = :id")
                query.bindValue(":id", id)
                query.bindValue(":name", newname)
                query.exec()
                if query.lastError().isValid():
                    log.error(f"Problem in editBaseName() update query: {query.lastError().text()}")
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)
                if self.model.lastError().isValid():
                    log.error(f"Problem in editBaseName() list refresh: {query.lastError().text()}")

                # Re-check linked pattern after name change
                linked_ref = parse_linked_object_name(newname)
                if linked_ref:
                    view_id, source_obj_id = linked_ref
                    linked_info = get_linked_object_info(view_id, source_obj_id)
                    if linked_info:
                        self.broken_link_ref = None
                        self.actionlist.set_linked_mode(linked_info, self._on_linked_mode_changed)
                    else:
                        # Pattern matched but object not found - this is a broken link
                        self.broken_link_ref = (view_id, source_obj_id)
                        self.actionlist.set_linked_mode(None, self._on_linked_mode_changed)
                        log.warning(
                            f"Object '{newname}' references non-existent object {source_obj_id} in view {view_id}"
                        )
                else:
                    self.broken_link_ref = None
                    self.actionlist.set_linked_mode(None, self._on_linked_mode_changed)

                self.actionlist.filterActions()
                self._update_linked_status_display()

                mark_db_as_changed()

    def updateTakeable(self, state):
        # state can be > 1, so convert to 1/0
        if state:
            checked = 1
        else:
            checked = 0
        self.updateCheckbox("Takeable", checked)

    def updateDraggable(self, state):
        # state can be > 1, so convert to 1/0
        if state:
            checked = 1
        else:
            checked = 0

        # When enabling draggable, check for overlap with other objects
        if checked and self.currentrow is not None:
            current_id = self.model.record(self.currentrow).value("Id")
            current_points_json = self.model.record(self.currentrow).value("Points")
            current_polygon = json_to_points(current_points_json)

            if current_polygon:
                # Check for overlap with other objects in this view
                has_overlap = False
                query = QtSql.QSqlQuery()
                query.prepare("SELECT Id, Points FROM objects WHERE Parent = :parent AND Id != :current_id")
                query.bindValue(":parent", self.parentid)
                query.bindValue(":current_id", current_id)
                query.exec()

                if query.isActive():
                    while query.next():
                        other_points_json = query.value(1)
                        other_polygon = json_to_points(other_points_json)
                        if other_polygon and polygons_overlap(current_polygon, other_polygon):
                            has_overlap = True
                            break

                if has_overlap:
                    # Show warning dialog
                    reply = QMessageBox.warning(
                        self.MainWindow,
                        "Overlapping Object Warning",
                        "This object partially or completely overlaps another object. "
                        "This may lead to the object still appearing in its original location "
                        "while it is being dragged, as well as after it has been placed in a pocket.\n\n"
                        "Are you sure you want to continue making this object draggable?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )

                    if reply == QMessageBox.StandardButton.No:
                        # Revert the checkbox without triggering the signal again
                        self.ui.draggable_checkBox.blockSignals(True)
                        self.ui.draggable_checkBox.setChecked(False)
                        self.ui.draggable_checkBox.blockSignals(False)
                        return

        self.updateCheckbox("Draggable", checked)

    def updateVisible(self, state):
        # state can be > 1, so convert to 1/0
        if state:
            checked = 1
        else:
            checked = 0
        self.updateCheckbox("Visible", checked)

    def updateCheckbox(self, columnname, checked):
        # update object record
        if self.currentrow is not None:
            id = self.model.record(self.currentrow).value("Id")
            query = QtSql.QSqlQuery()
            sqlstr = f"UPDATE {self.basetablename} SET {columnname.title()} = {int(checked)} WHERE Id = {id}"
            query.exec(sqlstr)
            if query.lastError().isValid():
                log.error(f"Problem in updateCheckbox() update query: {query.lastError().text()}")
            else:
                # reload model after change
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)

            mark_db_as_changed()

    # ── Tag management ──────────────────────────────────────────────

    def _refresh_tag_colors(self):
        if isinstance(self.model, TaggedSqlModel):
            self.model.set_tag_color_map(build_tag_color_map())

    def _get_existing_tags(self) -> list[str]:
        tags: set[str] = set()
        query = QtSql.QSqlQuery()
        query.exec("SELECT DISTINCT Tag FROM views WHERE Tag IS NOT NULL AND Tag != ''")
        while query.next():
            tags.add(str(query.value(0)).strip())
        query.exec("SELECT DISTINCT Tag FROM objects WHERE Tag IS NOT NULL AND Tag != ''")
        while query.next():
            tags.add(str(query.value(0)).strip())
        return sorted(tags)

    def _object_tag_context_menu(self, pos):
        index = self.ui.object_tableView.indexAt(pos)
        if not index.isValid():
            return

        row = index.row()
        _id = self.model.record(row).value("Id")
        current_tag = self.model.record(row).value("Tag") or ""

        menu = QtWidgets.QMenu(self.MainWindow)
        set_action = menu.addAction("Set Tag...")
        remove_action = menu.addAction("Remove Tag")
        remove_action.setEnabled(bool(str(current_tag).strip()))

        chosen = menu.exec(self.ui.object_tableView.viewport().mapToGlobal(pos))

        if chosen == set_action:
            self._set_object_tag(_id, str(current_tag).strip())
        elif chosen == remove_action:
            self._remove_object_tag(_id)

    def _set_object_tag(self, obj_id: int, current_tag: str):
        existing_tags = self._get_existing_tags()
        current_index = existing_tags.index(current_tag) if current_tag in existing_tags else 0

        tag, ok = QtWidgets.QInputDialog.getItem(
            self.MainWindow,
            "Set Tag",
            "Choose or enter a tag:",
            existing_tags,
            current_index,
            True,
        )

        if ok and tag.strip():
            query = QtSql.QSqlQuery()
            query.prepare("UPDATE objects SET Tag = :tag WHERE Id = :id")
            query.bindValue(":tag", tag.strip())
            query.bindValue(":id", obj_id)
            query.exec()
            if query.lastError().isValid():
                log.error(f"Problem setting tag: {query.lastError().text()}")
                return

            sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
            self.model.setQuery(sql)
            self._refresh_tag_colors()
            self._select_object_by_id(obj_id)
            mark_db_as_changed()

    def _remove_object_tag(self, obj_id: int):
        query = QtSql.QSqlQuery()
        query.prepare("UPDATE objects SET Tag = :tag WHERE Id = :id")
        query.bindValue(":tag", "")
        query.bindValue(":id", obj_id)
        query.exec()
        if query.lastError().isValid():
            log.error(f"Problem removing tag: {query.lastError().text()}")
            return

        sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
        self.model.setQuery(sql)
        self._refresh_tag_colors()
        self._select_object_by_id(obj_id)
        mark_db_as_changed()

    # ── Model setup ──────────────────────────────────────────────

    def initializeBaseModel(self, model, query):
        model.setQuery(query)
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Id")
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "Parent")
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, "Name")
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, "Points")
        model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, "Visible")
        model.setHeaderData(5, QtCore.Qt.Orientation.Horizontal, "Takeable")
        model.setHeaderData(6, QtCore.Qt.Orientation.Horizontal, "Draggable")
        model.setHeaderData(7, QtCore.Qt.Orientation.Horizontal, "Tag")
        model.setHeaderData(8, QtCore.Qt.Orientation.Horizontal, "RowOrder")

    def connectBaseModelToTableView(self, model, view):
        view.setModel(model)
        view.hideColumn(0)  # Id
        view.hideColumn(1)  # Parent
        # view.hideColumn(2)  # Name - visible
        view.hideColumn(3)  # Points (JSON string, not human-readable)
        view.hideColumn(4)  # Visible
        view.hideColumn(5)  # Takeable
        view.hideColumn(6)  # Draggable
        view.hideColumn(7)  # Tag
        view.hideColumn(8)  # RowOrder
        view.resizeColumnsToContents()

    def getParentInfo(self):
        query = QtSql.QSqlQuery()
        query.prepare("select Name, Foreground from views where Id = :id")
        query.bindValue(":id", self.parentid)
        query.exec()
        if query.isActive():
            query.first()
            self.parentname = query.value(0)
            self.parent_fg_pic = query.value(1)
            if self.parentname is None or self.parent_fg_pic is None:
                log.error(
                    f"Problem in getParentInfo(): parent name ({self.parentname}) "
                    f"or foregroundpic ({self.parent_fg_pic}) is type None"
                )
                return  # was quit()...why?
            elif not os.path.isfile(os.path.join(self.mediapath, self.parent_fg_pic)):
                log.error(
                    f"Problem in getParentInfo(): parent foreground picture ({self.parent_fg_pic}) is inaccessible."
                )
                return  # was quit()...why?
            else:
                self.parent_fg_pic = os.path.join(self.mediapath, self.parent_fg_pic)
        else:
            log.error(
                f"Problem in getParentInfo(): unable to read parent information "
                f"(id={self.parentid}) from the views database."
            )
            return  # was quit()...why?

    def initializeDatabases(self):
        self.model = TaggedSqlModel(tag_column_index=7)
        self.initializeBaseModel(
            self.model,
            f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder",
        )
        self.connectBaseModelToTableView(self.model, self.ui.object_tableView)
        self._refresh_tag_colors()

    def initializeViews(self):
        # if there is anything in the base list, select the first one
        if self.model.rowCount() > 0:
            obj_id = self.model.record(0).value("Id")
            obj_name = self.model.record(0).value("Name")
            # select first row
            self.ui.object_tableView.selectRow(0)
            self.currentrow = 0
            # make sure checkboxes are current
            # - note: slots don't need to be disabled here because they are not connected until after db init!
            self.ui.visible_checkBox.setChecked(self.model.record(0).value("Visible"))
            self.ui.takeable_checkBox.setChecked(self.model.record(0).value("Takeable"))
            self.ui.draggable_checkBox.setChecked(self.model.record(0).value("Draggable"))
            # load any corresponding actions
            self.actionlist = action_list.ActionList(obj_id, self.ui.OAL_tableView, "object", media_path=self.mediapath)
            self.actionlist.parent_id = obj_id

            # Check if this object has a linked action name pattern
            linked_ref = parse_linked_object_name(obj_name)
            if linked_ref:
                view_id, source_obj_id = linked_ref
                linked_info = get_linked_object_info(view_id, source_obj_id)
                if linked_info:
                    self.broken_link_ref = None
                    self.actionlist.set_linked_mode(linked_info, self._on_linked_mode_changed)
                else:
                    # Pattern matched but object not found - this is a broken link
                    self.broken_link_ref = (view_id, source_obj_id)
                    log.warning(f"Object '{obj_name}' references non-existent object {source_obj_id} in view {view_id}")
            else:
                self.broken_link_ref = None

            self.actionlist.filterActions()
            self._update_linked_status_display()
            # handle pic fields
            self.loadPicFields()
        # This clause just added to fix problem loading objects win when there are no objects
        else:
            self.actionlist = action_list.ActionList(None, self.ui.OAL_tableView, "object", media_path=self.mediapath)
            self.actionlist.parent_id = None

        # setup selection model handler (mouse or keyboard)...have to do *after* table is filled: http://goo.gl/KPaajQ
        self.selectionmodel = self.ui.object_tableView.selectionModel()
        self.selectionmodel.selectionChanged.connect(self.handleSelectionChange)

        # throw up the parent view name just so we know
        self.ui.parent_Label.setText(self.parentname)
