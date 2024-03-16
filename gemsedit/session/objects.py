from PySide6.QtGui import QGuiApplication

import gemsedit.gui.objects_window as win
from PySide6 import QtCore, QtGui, QtWidgets, QtSql
from gemsedit.gui import ACTIONLIST, object_select_widget as objselect
import os
import re
from gemsedit.database.connection import mark_db_as_changed
from gemsedit import log

from gemsedit import dialog_font
from gemsedit.gui.custom_messagebox import CustomMessageBox

# Todo: when entering actions, sometimes the object list selection goes somewhere else.
from gemsedit.database.sqltools import get_next_value


class objects:
    def __init__(self, parentid, mediapath, parent_win):

        self.parentid = parentid
        self.mediapath = mediapath
        self.parent_win = parent_win
        self.parentname = None
        self.parentfgpic = None

        self.model = None
        self.currentrow = None
        self.basename = "Object"
        self.basetablename = "objects"

        self.MainWindow = QtWidgets.QDialog()
        self.ui = win.Ui_ObjectsWindow()
        self.ui.setupUi(self.MainWindow)
        self.selectionmodel = None
        self.objbox = self.create_box(
            self.ui.objectLocPic_label, 0, 0, 0, 0, "yellow", "ObjectBox"
        )

        self.actionlist = None

        self.getParentInfo()
        self.initializeDatabases()
        self.initializeViews()
        self.connectSlots()

        self.center()

    def center(self):
        qr = self.MainWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.MainWindow.move(qr.topLeft())

    def closeTheWindow(self):
        self.parent_win.show()
        self.MainWindow.close()

    def connectSlots(self):
        self.ui.object_tableView.doubleClicked.connect(self.handleBaseDoubleClick)
        self.ui.objectAdd_toolButton.pressed.connect(self.handleBaseAdd)
        self.ui.objectDel_toolButton.pressed.connect(self.handleBaseDel)
        self.ui.OAL_tableView.clicked.connect(self.handleActionClick)
        self.ui.actionAdd_toolButton.pressed.connect(self.actionlist.handleActionAdd)
        self.ui.actionDel_toolButton.pressed.connect(self.actionlist.handleActionDel)
        self.ui.takeable_checkBox.toggled.connect(self.updateTakeable)
        self.ui.draggable_checkBox.toggled.connect(self.updateDraggable)
        self.ui.visible_checkBox.toggled.connect(self.updateVisible)
        self.ui.delSelect_toolButton.pressed.connect(
            lambda: self.handlePicEdit(mode="delete")
        )
        self.ui.drawSelect_toolButton.pressed.connect(
            lambda: self.handlePicEdit(mode="select")
        )

        self.ui.objectLocPic_label.signalClicked.connect(
            lambda: self.handlePicEdit(mode="viewonly")
        )

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
            self.selectionmodel.select(
                sel, QtCore.QItemSelectionModel.SelectionFlag.Select
            )
            self.ui.object_tableView.selectRow(curr_row)

    def handlePicEdit(self, mode):
        left = 0
        top = 0
        width = 0
        height = 0
        if mode == "delete":
            left = top = width = height = 0
        elif mode == "select":
            if self.parentid is None or self.currentrow is None:
                return
            self.MainWindow.hide()
            id = self.model.record(self.currentrow).value("Id")
            objSelector = objselect.ObjectSelect(
                current_view=self.parentid,
                current_obj=id,
                allow_selection=True,
                media_path=self.mediapath,
            )
            objSelector.showMaximized()
            objSelector.exec()
            self.MainWindow.show()
            if objSelector.result is not None:
                left, top, right, bottom, width, height = objSelector.result
                query = QtSql.QSqlQuery()
                sql = (
                    f"UPDATE {self.basetablename}"
                    f" SET Left = :left, Top = :top, Width = :width, Height = :height WHERE Id = :id"
                )
                query.prepare(sql)
                query.bindValue(":left", left)
                query.bindValue(":top", top)
                query.bindValue(":width", width)
                query.bindValue(":height", height)
                query.bindValue(":id", id)
                query.exec()
                if query.lastError().isValid():
                    log.error(
                        f"Problem in handlePicEdit() update query: {query.lastError().text()}"
                    )
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)
                self.loadPicFields()
        elif mode == "viewonly":
            self.MainWindow.hide()
            id = self.model.record(self.currentrow).value("Id")
            objSelector = objselect.ObjectSelect(
                current_view=self.parentid,
                current_obj=id,
                allow_selection=False,
                view_pic="Foreground",
                media_path=self.mediapath,
            )
            objSelector.showMaximized()
            objSelector.exec()
            self.MainWindow.show()
        else:
            return

        self.reinstateViewSelection()

        mark_db_as_changed()

    def create_box(self, targetobject, left, top, width, height, colorname, name="Box"):
        colordict = {
            "red": "rgb(255, 0, 0)",
            "green": "rgb(0, 255, 0)",
            "blue": "rgb(0, 0, 255)",
            "yellow": "rgb(255, 255, 0)",
        }
        selectBox = QtWidgets.QFrame(targetobject)
        selectBox.setEnabled(True)
        selectBox.setGeometry(QtCore.QRect(left, top, width, height))
        selectBox.setStyleSheet(f"color: {colordict[str(colorname)]};")
        selectBox.setFrameShape(QtWidgets.QFrame.Shape.Box)
        selectBox.setFrameShadow(QtWidgets.QFrame.Shadow.Plain)
        selectBox.setLineWidth(3)
        selectBox.setObjectName(str(name))
        return selectBox

    def clearPicFields(self):
        self.ui.objectLocPic_label.clear()  # .setPixmap(None)
        self.ui.objectPic_label.clear()  # .setPixmap(None)
        self.objbox.setGeometry(0, 0, 0, 0)

    def loadPicFields(self):
        if self.currentrow is None or self.model.rowCount() == 0:
            self.clearPicFields()
            return

        # get object info
        id = self.model.record(self.currentrow).value("Id")
        Name = self.model.record(self.currentrow).value("Name")
        Parent = self.model.record(self.currentrow).value("Parent")
        Left = self.model.record(self.currentrow).value("Left")
        Top = self.model.record(self.currentrow).value("Top")
        Width = self.model.record(self.currentrow).value("Width")
        Height = self.model.record(self.currentrow).value("Height")
        Visible = self.model.record(self.currentrow).value("Visible")
        Takeable = self.model.record(self.currentrow).value("Takeable")
        Draggable = self.model.record(self.currentrow).value("Draggable")

        # show big overview image
        if os.path.exists(self.parentfgpic):
            fgpixmap = QtGui.QPixmap(self.parentfgpic)
            self.ui.objectLocPic_label.setPixmap(fgpixmap)
            self.ui.objectLocPic_label.setScaledContents(True)
            labelwidth = self.ui.objectLocPic_label.width()
            labelheight = self.ui.objectLocPic_label.height()
            xl = float(Left) / float(fgpixmap.width())
            xt = float(Top) / float(fgpixmap.height())
            xw = float(Width) / float(fgpixmap.width())
            xh = float(Height) / float(fgpixmap.height())
            self.objbox.setGeometry(
                int(xl * labelwidth),
                int(xt * labelheight),
                int(xw * labelwidth),
                int(xh * labelheight),
            )
        else:
            self.ui.objectLocPic_label.clear()  # .setPixmap(None)

        # show object image
        if os.path.exists(self.parentfgpic):
            objPixmap = QtGui.QPixmap(self.parentfgpic).copy(Left, Top, Width, Height)
            self.ui.objectPic_label.clear()  # .setPixmap(None)
            self.ui.objectPic_label.setPixmap(objPixmap)
            self.ui.objectPic_label.setScaledContents(True)
        else:
            self.ui.objectPic_label.clear()  # .setPixmap(None)

    # Note: connected to listview *after* list is filled from db
    def handleSelectionChange(self, selected, deselected):
        try:
            # get some required info
            row = QtCore.QItemSelection(selected).indexes()[0].row()
            id = (
                QtCore.QItemSelection(selected)
                .indexes()[0]
                .model()
                .record(row)
                .value("Id")
            )
            visible = (
                QtCore.QItemSelection(selected)
                .indexes()[0]
                .model()
                .record(row)
                .value("Visible")
            )
            takeable = (
                QtCore.QItemSelection(selected)
                .indexes()[0]
                .model()
                .record(row)
                .value("Takeable")
            )
            draggable = (
                QtCore.QItemSelection(selected)
                .indexes()[0]
                .model()
                .record(row)
                .value("Draggable")
            )

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
            self.actionlist.parent_id = id
            self.actionlist.filterActions()

            self.loadPicFields()
        except Exception as e:
            log.error(
                f"Problem in handleSelectionChange({selected}, {deselected}): {e}"
            )

    def handleBaseDoubleClick(self, index):
        # id =  self.getIdFromClick(index)
        # name = self.getNameFromClick(index)
        id = index.model().record(index.row()).value("Id")
        name = index.model().record(index.row()).value("Name")
        self.editBaseName(id, name)

    def handleBaseAdd(self):
        bn = self.basename.title()
        newid = get_next_value(
            column_name="Id", table_name=self.basename.lower() + "s", default=0
        )
        neworder = get_next_value(
            column_name="RowOrder", table_name=self.basename.lower() + "s", default=0
        )
        newname = f"New{bn}{newid}"

        # get list of old names
        namelist = []
        query = QtSql.QSqlQuery()
        query.exec(
            f"select Name from {self.basetablename} where Parent = {self.parentid}"
        )
        if query.isActive():
            while query.next():
                namelist.append(query.value(0))

        text = "???"
        newname = text
        ok = True
        while ok is True and (
            (not self.strIsPattern(newname, "\w*")) or (newname in namelist)
        ):
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                "Adding New " + bn,
                "Enter an " + bn + " name (alpha numeric only, no spaces):",
            )
            newname = str(text)
            if ok:
                if not self.strIsPattern(newname, "\w*"):  # newname.isalpha():
                    _ = CustomMessageBox.information(
                        self.parent_win,
                        "Bad Object Name",
                        "Object Name Error: Name must consist of only characters from this "
                        "set: [a-zA-Z0-9_]. Please choose another name.",
                        font=dialog_font,
                    )
                elif newname in namelist:
                    _ = CustomMessageBox.information(
                        self.parent_win,
                        "Bad Object Name",
                        f'Object Name Error: An object called "{newname}" already exists in '
                        f'"{self.parentname}". Please choose another name.',
                        font=dialog_font,
                    )

        if ok:
            newname = str(text)
            query = QtSql.QSqlQuery()
            query.prepare(
                "INSERT INTO "
                "objects (Id, Parent, Name, Left, Top, Width, Height, Visible, Takeable, Draggable, RowOrder) "
                "VALUES "
                "(:id, :parent, :name, :left, :top, :width, :height, :visible, :takeable, :draggable, :roworder)"
            )
            query.bindValue(":id", newid)
            query.bindValue(":parent", self.parentid)
            query.bindValue(":name", newname)
            query.bindValue(":left", 0)
            query.bindValue(":top", 0)
            query.bindValue(":width", 1)
            query.bindValue(":height", 1)
            query.bindValue(":visible", 1)
            query.bindValue(":takeable", 0)
            query.bindValue(":draggable", 0)
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
            ret = CustomMessageBox.question(
                self.MainWindow,
                f"Delete {bn} {name}",
                f"Really delete {name} and all of it's associated actions?",
                font=dialog_font,
                buttons=QtWidgets.QMessageBox.StandardButton.Cancel
                | QtWidgets.QMessageBox.StandardButton.Ok,
                default_button=QtWidgets.QMessageBox.StandardButton.Cancel,
            )

            if ret == QtWidgets.QMessageBox.StandardButton.Ok:
                # delete base
                query1 = QtSql.QSqlQuery()
                query1.prepare("DELETE FROM " + self.basetablename + " where Id = :id")
                query1.bindValue(":id", id)
                query1.exec()
                if query1.lastError().isValid():
                    log.error(
                        f"Problem in handleBaseDel(): {query1.lastError().text()}"
                    )
                else:
                    # delete associated actions for base
                    query2 = QtSql.QSqlQuery()
                    query2.prepare(
                        "DELETE FROM actions where ContextType = :actiontype and ContextId = :id"
                    )
                    query2.bindValue(":actiontype", self.basename.lower())
                    query2.bindValue(":id", id)
                    query2.exec()
                    if query2.lastError().isValid():
                        log.error(
                            f"Problem in handleBaseDel(): {query1.lastError().text()}"
                        )
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

    def editBaseName(self, id, name):
        bn = self.basename.title()
        # get list of old names
        namelist = []
        query = QtSql.QSqlQuery()
        query.exec("select Name from " + self.basetablename)
        if query.isActive():
            while query.next():
                namelist.append(query.value(0))
        if name in namelist:
            namelist.remove(name)
        # get the name
        text = "???"
        newname = text
        ok = True

        while ok is True and (
            (not self.strIsPattern(newname, "\w*")) or (newname in namelist)
        ):
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                f"Change {bn} Name",
                f"Enter an {bn.lower()} name (alpha numeric only, no spaces):",
                text=name,
            )
            newname = str(text)
            if ok:
                if not self.strIsPattern(newname, "\w*"):
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
                query = QtSql.QSqlQuery()
                query.prepare(
                    "UPDATE " + self.basetablename + " SET Name = :name WHERE Id = :id"
                )
                query.bindValue(":id", id)
                query.bindValue(":name", newname)
                query.exec()
                if query.lastError().isValid():
                    log.error(
                        f"Problem in editBaseName() update query: {query.lastError().text()}"
                    )
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)
                if self.model.lastError().isValid():
                    log.error(
                        f"Problem in editBaseName() list refresh: {query.lastError().text()}"
                    )

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
                log.error(
                    f"Problem in updateCheckbox() update query: {query.lastError().text()}"
                )
            else:
                # reload model after change
                sql = f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder"
                self.model.setQuery(sql)

            mark_db_as_changed()

    def initializeBaseModel(self, model, query):
        model.setQuery(query)
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Id")
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "Parent")
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, "Name")
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, "Left")
        model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, "Top")
        model.setHeaderData(5, QtCore.Qt.Orientation.Horizontal, "Width")
        model.setHeaderData(6, QtCore.Qt.Orientation.Horizontal, "Height")
        model.setHeaderData(7, QtCore.Qt.Orientation.Horizontal, "Visible")
        model.setHeaderData(8, QtCore.Qt.Orientation.Horizontal, "Takeable")
        model.setHeaderData(9, QtCore.Qt.Orientation.Horizontal, "Draggable")
        model.setHeaderData(10, QtCore.Qt.Orientation.Horizontal, "RowOrder")

    def connectBaseModelToTableView(self, model, view):
        view.setModel(model)
        view.hideColumn(0)  # Id
        view.hideColumn(1)  # Parent
        # view.hideColumn(2) #Name
        view.hideColumn(3)  # Left
        view.hideColumn(4)  # Top
        view.hideColumn(5)  # Width
        view.hideColumn(6)  # Height
        view.hideColumn(7)  # Visible
        view.hideColumn(8)  # Takeable
        view.hideColumn(9)  # Draggable
        view.hideColumn(10)  # RowOrder
        view.resizeColumnsToContents()

    def getParentInfo(self):
        query = QtSql.QSqlQuery()
        query.prepare("select Name, Foreground from views where Id = :id")
        query.bindValue(":id", self.parentid)
        query.exec()
        if query.isActive():
            query.first()
            self.parentname = query.value(0)
            self.parentfgpic = query.value(1)
            if self.parentname is None or self.parentfgpic is None:
                log.error(
                    f"Problem in getParentInfo(): parent name ({self.parentname}) "
                    f"or foregroundpic ({self.parentfgpic}) is type None"
                )
                return  # was quit()...why?
            elif not os.path.isfile(os.path.join(self.mediapath, self.parentfgpic)):
                log.error(
                    f"Problem in getParentInfo(): parent foreground picture ({self.parentfgpic}) is inaccessible."
                )
                return  # was quit()...why?
            else:
                self.parentfgpic = os.path.join(self.mediapath, self.parentfgpic)
        else:
            log.error(
                f"Problem in getParentInfo(): unable to read parent information "
                f"(id={self.parentid}) from the views database."
            )
            return  # was quit()...why?

    def initializeDatabases(self):
        self.model = QtSql.QSqlQueryModel()  # CustomSqlModel()
        self.initializeBaseModel(
            self.model,
            f"select * from {self.basetablename} where Parent = {self.parentid} order by RowOrder",
        )
        self.connectBaseModelToTableView(self.model, self.ui.object_tableView)
        # from gemsedit import log
        # self.model.dataChanged.connect(lambda x: partial(log.debug, "objects 514 data changed"))

    def initializeViews(self):
        # if there is anything in the base list, select the first one
        if self.model.rowCount() > 0:
            id = self.model.record(0).value("Id")
            # select first row
            self.ui.object_tableView.selectRow(0)
            self.currentrow = 0
            # make sure checkboxes are current
            # - note: slots don't need to be disabled here because they are not connected until after db init!
            self.ui.visible_checkBox.setChecked(self.model.record(0).value("Visible"))
            self.ui.takeable_checkBox.setChecked(self.model.record(0).value("Takeable"))
            self.ui.draggable_checkBox.setChecked(
                self.model.record(0).value("Draggable")
            )
            # load any corresponding actions
            self.actionlist = ACTIONLIST.ActionList(
                id, self.ui.OAL_tableView, "object", mediapath=self.mediapath
            )
            self.actionlist.parent_id = id
            self.actionlist.filterActions()
            # handle pic fields
            self.loadPicFields()
        # This clause just added to fix problem loading objects win when there are no objects
        else:
            self.actionlist = ACTIONLIST.ActionList(
                None, self.ui.OAL_tableView, "object", mediapath=self.mediapath
            )
            self.actionlist.parent_id = None

        # setup selection model handler (mouse or keyboard)...have to do *after* table is filled: http://goo.gl/KPaajQ
        self.selectionmodel = self.ui.object_tableView.selectionModel()
        self.selectionmodel.selectionChanged.connect(self.handleSelectionChange)

        # throw up the parent view name just so we know
        self.ui.parent_Label.setText(self.parentname)
