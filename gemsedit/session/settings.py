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

from collections.abc import Callable

from PySide6 import QtCore, QtSql, QtWidgets
from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    # QItemSelection,
    # QItemSelectionModel,
    Qt,
)
from PySide6.QtGui import QGuiApplication, QMouseEvent
from PySide6.QtWidgets import QMainWindow, QTableView

from gemsedit import log
from gemsedit.database.connection import mark_db_as_changed
from gemsedit.gui import helptext, mycolors
import gemsedit.gui.genericrowdelegates as generic_row_delegates
import gemsedit.gui.settings_dlg as win


class SettingsListModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings_list: list | None = None
        self._view_dict = {}
        self._signal_update: Callable | None = None

    def initData(
        self,
        settings_list: list,
        view_dict: dict | None = None,
        signal_update: Callable | None = None,
    ):
        self._settings_list = settings_list
        self._view_dict = view_dict
        if signal_update is not None:
            self._signal_update = signal_update

    def rowCount(self, parent=QtCore.QModelIndex()):  # noqa: B008
        try:
            return len(self._settings_list)
        except:
            return 0

    def columnCount(self, index=QtCore.QModelIndex()):  # noqa: B008
        return 1

    def headerData(
        self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole
    ):  # was role: int = ...
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            if orientation == QtCore.Qt.Orientation.Vertical:
                return int(QtCore.Qt.AlignmentFlag.AlignRight)
            return int(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Vertical:
            if self._settings_list:
                return self._settings_list[section][1]  # Settings Name
        return section + 1

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        # try:
        #     log.debug(f"{index.row()=} {index.column()=} {value=}")
        # except:
        #     ...

        # NOTE: this works, but is a kludge until I can figure out how to construct a proper index
        #  with row=5 and col=2, I tried, but I keep getting -1, -1.
        if value == "Clear Global Overlay" and role == QtCore.Qt.ItemDataRole.EditRole:
            self._settings_list[5][2] = ""
            self.dataChanged.emit(index, index)
            if self._signal_update is not None:
                self._signal_update()
            return True

        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            row = index.row()
            v = value

            if index.row() == 0:  # >>>>>> view id
                log.warning("NOTE: GEMSedit is not allowing the view Id setting to be changed at the moment.")
                return False

            elif index.row() == 1:  # >>>>>> start view
                if ":" in str(v):
                    v = int(v.split(":")[0])

            elif index.row() == 3:  # >>>>>> view transitions
                if str(v).title() in ("None", "Fade"):
                    v = str(v).title()
                else:
                    v = "None"

            elif index.row() == 4:  # >>>>>> preload resources
                if str(v).title() in ("True", "1"):
                    v = 1
                else:
                    v = 0

            elif index.row() == 6:  # >>>>>> gemsrun version
                log.warning(
                    "NOTE: GEMSedit will automatically update the GEMSedit version when you next save your environment."
                )
                return False

            self._settings_list[row][2] = v  # Settings Value

            # self.emit(QtCore.SIGNAL("dataChanged(QModelIndex,QModelIndex)"), index, index)
            self.dataChanged.emit(index, index)
            if self._signal_update is not None:
                self._signal_update()
            return True

        return False

    def flags(self, index):
        flag = QAbstractTableModel.flags(self, index)
        # 0 is Env ID, 6 is GEMSedit Version, neither is not to be user editable
        # flag |= Qt.ItemFlag.ItemIsEditable if index.row() not in (0, 6) else (not Qt.ItemFlag.ItemIsEditable)
        if index.row() not in (0, 6):
            flag |= Qt.ItemFlag.ItemIsEditable
        return flag

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        # try:
        #     log.debug(f"{index.row()=} {index.column()=}")
        # except:
        #     ...

        if not index.isValid() or not 0 <= index.row() < self.rowCount() or not self._settings_list:
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            disp_value = self._settings_list[index.row()][2]

            if index.row() == 1:  # >>>>>> start view
                try:
                    disp_value = f"{disp_value}:{self._view_dict[str(disp_value)]}"
                except:
                    pass
            elif index.row() == 4:  # >>>>>> preload resources
                try:
                    if int(disp_value):
                        disp_value = "True"
                    else:
                        disp_value = "False"
                except ValueError:
                    disp_value = "False"
            return disp_value  # Settings Value

        return None


# (Id INT PRIMARY KEY UNIQUE, Startview INT, Pocketcount INT,  Roomtrasition TEXT, Preloadresources INT,
# Globaloverlay TEXT, Version REAL)


class Settings:
    def __init__(self, media_path: str, parent_win: QMainWindow):
        self.media_path = media_path
        self.parent_win = parent_win
        self.model: SettingsListModel | None = None
        self.selection_model = None
        self.settings_list = []
        self.help_dict = {}
        self.viewlist = []
        self.view_dict = {}
        self.trans_list = []
        self.color_list = []
        self.display_list = []
        self.hover_list = []
        self.current_id = None

        self.MainWindow = QtWidgets.QDialog()
        self.ui = win.Ui_SettingsDialog()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.setModal(False)

        self.load_lists()
        self.help_dict = helptext.settings_desc
        self.connect_slots()
        self.populate_settings_list()
        # self.ui.clearOverlay.connect(self.handleClearOverlay)

        self.result = "ApplyDialogChangesPlease"

        self.center()

    def center(self):
        qr = self.MainWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.MainWindow.move(qr.topLeft())

    def load_lists(self):
        query = QtSql.QSqlQuery()

        # Views
        self.viewlist = []
        query.exec("select Id, Name from views")
        if query.isActive():
            # while next(query):
            while query.next():
                s = f"{str(query.value(0))}:{str(query.value(1))}"
                self.viewlist.append(s)

        self.view_dict = {}
        for x in self.viewlist:
            a, b = x.split(":")
            self.view_dict[str(a)] = str(b)

        # Translist
        tmp_dict = helptext.transistion_desc
        self.trans_list = []
        for key in tmp_dict:
            self.trans_list.append(key)

        # Colorlist
        # self.colorlist = mycolors.colors_small
        # self.colorlist = []
        # for color in mycolors.colors_large:
        #     self.colorlist.append(f"{color[0]}\t{color[2]}")
        self.color_list = []
        for color in mycolors.colors_large:
            self.color_list.append(f"['{str(color[0])}',{color[2][0]},{color[2][1]},{color[2][2]},255]")

        # Displaylist
        tmp_dict = helptext.display_desc
        self.display_list = []
        for key in tmp_dict:
            self.display_list.append(key)

        # HoverList
        tmp_dict = helptext.hover_desc
        self.hover_list = []
        for key in tmp_dict:
            self.hover_list.append(key)

        # Settings List
        # (Id INT PRIMARY KEY UNIQUE, Startview INT, Pocketcount INT,
        # Roomtransition TEXT, Preloadresources INT, Globaloverlay TEXT,
        # Version REAL, StageColor TEXT, DisplayType TEXT, ObjectHover TEXT)
        # 0|0|6|None|0||1.5|Black|Windowed|None
        self.settings_list = []
        query.exec("select * from options")
        if query.isActive():
            # while next(query):
            while query.next():
                self.settings_list.append(["number", "Id", query.value(0)])
                self.settings_list.append(["viewnum", "Start View", query.value(1)])
                self.settings_list.append(["number", "Pocket Count", query.value(2)])
                self.settings_list.append(["translist", "View Transition", query.value(3)])
                self.settings_list.append(["bool", "Preload Resources", query.value(4)])
                self.settings_list.append(
                    [
                        "picfile",
                        "Global Overlay\n(Right-Click To Clear)",
                        query.value(5),
                    ]
                )
                self.settings_list.append(["value", "GEMSedit Version", query.value(6)])
                self.settings_list.append(["colorlist", "Stage Color", query.value(7)])
                self.settings_list.append(["displaylist", "Display Type", query.value(8)])
                self.settings_list.append(["hoverlist", "Object Hover", query.value(9)])
                self.settings_list.append(["01float", "Media Volume", query.value(10)])

    def connect_slots(self):
        # QtCore.QObject.connect(self.ui.applyButton, QtCore.SIGNAL("pressed()"), self.handleApply)
        self.ui.applyButton.pressed.connect(self.handleApply)

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def handleApply(self):
        self.parent_win.show()
        # self.MainWindow.accept()
        self.MainWindow.close()

    def handleCancel(self):
        self.result = None
        # self.MainWindow.reject() # QtWidgets.QDialog.Rejected
        self.MainWindow.close()

    def signalUpdate(self):
        # in case you want to do something when there has been a data change
        # (Id INT PRIMARY KEY UNIQUE, Startview INT, Pocketcount INT,
        # Roomtransition TEXT, Preloadresources INT, Globaloverlay TEXT,
        # Version REAL, StageColor TEXT, DisplayType TEXT, ObjectHover TEXT)

        query = QtSql.QSqlQuery()
        sqlstr = (
            f"update options set Startview='{self.settings_list[1][2]}', "
            f"Pocketcount='{self.settings_list[2][2]}', "
            f"Roomtransition='{self.settings_list[3][2]}', "
            f"Preloadresources='{self.settings_list[4][2]}', "
            f"Globaloverlay='{self.settings_list[5][2]}', "
            f'StageColor="{self.settings_list[7][2]}", '
            f"DisplayType='{self.settings_list[8][2]}', "
            f"ObjectHover='{self.settings_list[9][2]}', "
            f"Volume='{self.settings_list[10][2]}' where Id = {0}"
        )

        query.exec(sqlstr)

        if query.lastError().isValid():
            log.error(f"Error in data update query: {query.lastError().text()}")

        mark_db_as_changed()

    def handle_clear_overlay(self, row, col):
        """
        Clear out global overlay image.
        :param row: row in table view that led here. Should always be 5. Not Used.
        :param col: col in the table view that led here. Should always be 0(?). Not Used.
        :return:
        """
        query = QtSql.QSqlQuery()
        sql_str = "update options set Globaloverlay='' where Id = 0"
        query.exec(sql_str)

        if query.lastError().isValid():
            log.error(f"Error in data update query: {query.lastError().text()}")
        else:
            self.load_lists()
            self.update_settings_info()

    def mouse_press_global_overlay_reset(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.RightButton:
            # index = self.model.index(6,1,QModelIndex())
            self.ui.settings_tableView.model().setData(
                self.ui.settings_tableView.model().index(5, 2, QModelIndex()),
                "Clear Global Overlay",
            )
        else:
            QTableView.mousePressEvent(self.ui.settings_tableView, event)

    def populate_settings_list(self):
        # create model
        self.model = SettingsListModel()
        if len(self.settings_list):
            self.model.initData(
                self.settings_list,
                view_dict=self.view_dict,
                signal_update=self.signalUpdate,
            )

        # add hook for deleting global overlay
        self.ui.settings_tableView.mousePressEvent = self.mouse_press_global_overlay_reset

        # attach model to view
        self.ui.settings_tableView.setModel(self.model)
        self.ui.settings_tableView.hideRow(0)  # don't let user see environment Id

        # create setting editing delegate with different editors depending on settings type
        delegate = generic_row_delegates.GenericRowDelegate()
        for i, x in enumerate(self.settings_list):
            type_item, setting_item, value_item = x  # unpack components
            # log.debug(f'{type_item=}, {setting_item=}, {value_item=}')

            if setting_item not in ("Id", "Version"):
                if type_item == "number":
                    delegate.insertRowDelegate(i, generic_row_delegates.IntegerRowDelegate(0, 6))
                elif type_item == "01float":
                    delegate.insertRowDelegate(i, generic_row_delegates.FloatRowDelegate(0.0, 1.0))
                elif type_item == "value":
                    delegate.insertRowDelegate(i, generic_row_delegates.PlainTextRowDelegate())
                elif type_item == "viewnum":
                    delegate.insertRowDelegate(i, generic_row_delegates.ComboRowDelegate(self.viewlist))
                elif type_item == "translist":
                    delegate.insertRowDelegate(i, generic_row_delegates.ComboRowDelegate(self.trans_list))
                elif type_item == "colorlist":
                    delegate.insertRowDelegate(
                        i,
                        generic_row_delegates.ComboRowColoredDelegate(self.color_list),
                    )
                elif type_item == "displaylist":
                    delegate.insertRowDelegate(i, generic_row_delegates.ComboRowDelegate(self.display_list))
                elif type_item == "hoverlist":
                    delegate.insertRowDelegate(i, generic_row_delegates.ComboRowDelegate(self.hover_list))
                elif type_item == "bool":
                    onoff = ["False", "True"]
                    delegate.insertRowDelegate(i, generic_row_delegates.ComboRowDelegate(onoff))
                elif type_item == "picfile":
                    pic_filter = "PictureFile (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)"
                    delegate.insertRowDelegate(
                        i,
                        generic_row_delegates.FileRowDelegate(self.media_path, pic_filter),
                    )
                # otherwise, should evoke default delegate

                # associated delegate with settings table view
                self.ui.settings_tableView.setItemDelegate(delegate)

        # other table view config
        self.ui.settings_tableView.resizeColumnsToContents()
        self.ui.settings_tableView.resizeRowsToContents()

        # setup selection model handler (mouse or keyboard)...have to do *after* table is filled: http://goo.gl/KPaajQ
        self.selection_model = self.ui.settings_tableView.selectionModel()
        self.selection_model.selectionChanged.connect(self.handle_selection_change)

        self.ui.settings_tableView.setAlternatingRowColors(True)

        # force selection of first row (otherwise dialog crashes on resize?!) vvv not working!
        # index = self.ui.settings_tableView.model().index(0,2)
        # self.ui.settings_tableView.selectionModel().select(index, QItemSelectionModel.SelectionFlag.Select)

    def handle_selection_change(self, selected, deselected):
        """Note: connected to listview *after* list is filled from db"""
        try:
            id = QtCore.QItemSelection(selected).indexes()[0].row()
            self.current_id = id
            self.update_settings_info()
        except Exception as e:
            log.exception(e)
            self.current_id = None

    def update_settings_info(self):
        # other table view config
        self.ui.settings_tableView.resizeColumnsToContents()
        self.ui.settings_tableView.resizeRowsToContents()

        if self.current_id:
            # data = self.settings_list[self.current_id][2]
            name = self.settings_list[self.current_id][1]
            self.ui.xxHelpLabel.setText(self.help_dict[name] if name else "")
