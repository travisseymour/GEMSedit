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

from PySide6 import QtCore, QtWidgets
from PySide6.QtCore import Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMainWindow

from gemsedit.gui import action_list
import gemsedit.gui.globalact_window as win


class MagicModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._settings_list = None
        self._view_dict: dict = {}

    def initData(self, settings_list, view_dict=None, signal_update=None):
        self._settings_list = settings_list
        self._view_dict = view_dict
        if signal_update is not None:
            self._signalupdate = signal_update

    def rowCount(self, parent=QtCore.QModelIndex()):
        try:
            return len(self._settings_list)
        except:
            return 0

    def columnCount(self, index=QtCore.QModelIndex()):
        # was (self, index=QtCore.QModelIndex())
        return 1

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):  # was role: int = ...
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
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:  # and
            row = index.row()
            v = value

            if index.row() == 0:  # >>>>>> start view
                try:
                    if v.find(":") > -1:
                        v = int(v.split(":")[0])
                except:
                    pass
            elif index.row() == 3:  # >>>>>> preload resources
                try:
                    if v == "True":
                        v = 1
                    elif v == "False":
                        v = 0
                except:
                    pass

            self._settings_list[row][2] = v  # Settings Value

            self.dataChanged.emit(index, index)
            if self._signalupdate is not None:
                self._signalupdate()
            return True
        return False

    def flags(self, index):
        flag = QtCore.QAbstractTableModel.flags(self, index)
        flag |= QtCore.Qt.ItemFlag.ItemIsEditable
        return flag

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount() or not self._settings_list:
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            try:
                display_value = self._settings_list[index.row()][2]
                if index.row() == 0:  # >>>>>> start view
                    try:
                        display_value = f"{display_value}:{self._view_dict[str(display_value)]}"
                    except:
                        pass
                elif index.row() == 3:  # >>>>>> preload resources
                    try:
                        if int(display_value) == 0:
                            display_value = "False"
                        elif int(display_value) == 1:
                            display_value = "True"
                    except:
                        pass
                return display_value  # Settings Value
            except:
                return None
        return None


class GlobalAct:
    def __init__(self, media_path: str, parent_win: QMainWindow):
        self.media_path = media_path
        self.parent_win = parent_win
        self.MainWindow = QtWidgets.QWidget()
        self.ui = win.Ui_GlobalActionsDialog()
        self.ui.setupUi(self.MainWindow)

        self.ui.GAL_tableView.setModel(None)
        self.ui.PAL_tableView.setModel(None)
        self.action_list_ga = action_list.ActionList(0, self.ui.GAL_tableView, "global", media_path=self.media_path)
        self.action_list_pa = action_list.ActionList(0, self.ui.PAL_tableView, "pocket", media_path=self.media_path)

        self.initializeViews()

        self.result = "ApplyDialogChangesPlease"

        self.connectSlots()

        self.center()

    def center(self):
        qr = self.MainWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.MainWindow.move(qr.topLeft())

    def connectSlots(self):
        self.ui.closeButton.pressed.connect(self.handleApply)
        # self.ui.cancelButton.pressed.connect(self.handleCancel)

        self.ui.GAL_tableView.clicked.connect(self.ga_handleActionClick)
        self.ui.PAL_tableView.clicked.connect(self.pa_handleActionClick)
        self.ui.gaAdd_toolButton.pressed.connect(self.action_list_ga.handleActionAdd)
        self.ui.gaDel_toolButton.pressed.connect(self.action_list_ga.handleActionDel)
        self.ui.paAdd_toolButton.pressed.connect(self.action_list_pa.handleActionAdd)
        self.ui.paDel_toolButton.pressed.connect(self.action_list_pa.handleActionDel)

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def handleApply(self):
        self.parent_win.show()
        self.MainWindow.close()

    def handleCancel(self):
        self.result = None
        self.parent_win.show()
        self.MainWindow.close()

    def getIdFromClick(self, index):
        return index.model().record(index.row()).value("Id")

    def ga_handleActionClick(self, index):
        id = self.getIdFromClick(index)
        self.action_list_ga.current_id = id

    def pa_handleActionClick(self, index):
        id = self.getIdFromClick(index)
        self.action_list_pa.current_id = id

    def initializeViews(self):
        self.action_list_ga.parent_id = 0
        self.action_list_pa.parent_id = 0
        self.action_list_ga.filterActions()
        self.action_list_pa.filterActions()
