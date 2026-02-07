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
from PySide6.QtCore import QModelIndex, Qt
from PySide6.QtGui import QCloseEvent, QColor, QGuiApplication

from gemsedit import log
from gemsedit.gui import genericrowdelegates, helptext, mycolors, mycursors, mykeys
import gemsedit.gui.param_select_dlg as win


class CustomSqlModel(QtSql.QSqlQueryModel):
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):  # Qt.DisplayRole as ...
        # value = super(CustomSqlModel, self).data(index, role)
        # if value is not None and role == QtCore.Qt.ItemDataRole.DisplayRole:
        #     if index.column() == 0:
        #         return '#%d' % value
        #     elif index.column() == 2:
        #         return value.upper()
        if role == Qt.ItemDataRole.ForegroundRole and index.column() == 0:
            return QColor(Qt.GlobalColor.blue)
        # if role == QtCore.Qt.ItemDataRole.ToolTipRole:
        #     return index.row()
        return super().data(index, role)


class ParamListModel(QtCore.QAbstractTableModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._param_dict: dict | None = None
        self._param_key: str = ""
        self._signal_update: Callable | None = None

    def initData(self, param_dict: dict, param_key: str, signal_update: Callable | None = None):
        # something like this: data=[['number', 'Seconds', '1000'],...]
        self._param_dict = param_dict
        self._param_key = param_key
        if signal_update is not None:
            self._signal_update = signal_update

    def rowCount(self, parent=QtCore.QModelIndex()):  # noqa: B008
        try:
            return len(self._param_dict[self._param_key])
        except:
            return 0

    def columnCount(self, index: QtCore.QModelIndex):
        return 1

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
        if role == QtCore.Qt.ItemDataRole.TextAlignmentRole:
            if orientation == QtCore.Qt.Orientation.Vertical:
                return int(QtCore.Qt.AlignmentFlag.AlignRight)
            return int(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        if role != QtCore.Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == QtCore.Qt.Orientation.Vertical:
            if self._param_dict:
                return self._param_dict[self._param_key][section][1]
        return section + 1

    def setData(self, index, value, role=QtCore.Qt.ItemDataRole.EditRole):
        if index.isValid() and role == QtCore.Qt.ItemDataRole.EditRole:
            row = index.row()
            self._param_dict[self._param_key][row][2] = value
            self.dataChanged.emit(index, index)
            if self._signal_update is not None:
                self._signal_update()
            return True
        else:
            return False

    def flags(self, index):
        flag = QtCore.QAbstractTableModel.flags(self, index)
        flag |= QtCore.Qt.ItemFlag.ItemIsEditable
        return flag

    def data(self, index, role=QtCore.Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < self.rowCount() or not self._param_dict:
            return None

        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            try:
                return str(self._param_dict[self._param_key][index.row()][2])
            except:
                return None

        return None


class ParamSelect:
    def __init__(self, param_type, param_string, action_type, media_path):
        self.xx_model: CustomSqlModel | None = None
        self.xx_param_model: ParamListModel | None = None
        self.current_xx_id = None
        self.param_type = str(param_type).title()
        self.param_string = param_string
        self.action_type = action_type
        self.media_path = media_path
        self.param_data_dict = {}
        self.help_dict = {}
        self.view_list = []
        self.obj_list = []
        self.color_list = []
        self.selection_model = None
        self.button_pressed = None
        self.ParmSelectWindow = QtWidgets.QWidget()
        self.ui = win.Ui_parameterSelectDialog()
        self.ui.setupUi(self.ParmSelectWindow)

        self.ui.titleLabel.setText(f"Action {self.param_type.title()} Editor")
        self.ui.xxLabel.setText(f"{self.param_type.title()} List")
        self.ui.xxparamLabel.setText(f"{self.param_type.title()} Parameter List")
        self.result = self.param_string
        self.ui.resultLabel.setText(f"{self.param_type.title()}: {self.result}")

        self.load_lists()
        self.setup_help_text()
        self.initializeDatabases()
        self.connectSlots()

        self.center()

        self.ParmSelectWindow.closeEvent = self.param_win_close

    def param_win_close(self, event: QCloseEvent) -> None:
        if self.button_pressed in (None, "cancel_button"):
            self.result = None

    def center(self):
        qr = self.ParmSelectWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.ParmSelectWindow.move(qr.topLeft())

    def getParamValueList(self):
        if self.param_string == "":
            return []

        param_string = self.param_string  # local copy

        v = "[" + param_string.split("(")[1]  # strip off command
        v = v.replace(")", "]")
        v = eval(v)  # convert params to list of params

        return v

    def connectSlots(self):
        self.ui.applyButton.pressed.connect(self.handleApply)
        self.ui.cancelButton.pressed.connect(self.handleCancel)

        QtCore.QMetaObject.connectSlotsByName(self.ParmSelectWindow)

    def getIdFromClick(self, index):
        return index.model().record(index.row()).value("Id")

    def getViewNameFromClick(self, index):
        return index.model().record(index.row()).value("Name")

    def handleApply(self):
        self.button_pressed = "apply_button"
        self.ParmSelectWindow.close()

    def handleCancel(self):
        self.button_pressed = "cancel_button"
        self.ParmSelectWindow.close()

    # Note: connected to listview *after* list is filled from db
    def handleSelectionChange(self, selected, deselected):
        id = QtCore.QItemSelection(selected).indexes()[0].row()
        self.current_xx_id = id
        self.populateParamList()

    def signalUpdate(self):
        self.result = self.constructParamString(human_readable=False)
        self.ui.resultLabel.setText(f"{self.param_type.title()}: {self.constructParamString(human_readable=True)}")

    def constructParamString(self, human_readable=False):
        index_list = self.ui.xx_tableView.selectedIndexes()
        index = index_list[0]
        name = str(index.data())
        param_str = ""

        try:
            param_list = self.param_data_dict[name]
            for i, x in enumerate(param_list):
                xx = str(x[2]).strip('"').strip("'")
                if not human_readable and ":" in xx:
                    xx = xx.split(":")[0].strip()
                if xx.isdigit() or xx.replace(".", "").isdigit() or xx in ("True", "False"):
                    param_str += xx
                else:
                    param_str += '"' + xx + '"'
                if (i + 1) < len(param_list):
                    param_str += ","
        except:
            param_str = ""

        if index.data() == "":
            s = ""
        else:
            s = str(index.data()) + f"({param_str})"
        return s

    def populateParamList(self):
        if self.current_xx_id is not None:
            # grab info about this type of xx from the database (actually get from data in xxmodel)
            initial_xx = self.param_string.split("(")[0]
            name = str(self.xx_model.record(self.current_xx_id).field("Name").value())
            template = str(self.xx_model.record(self.current_xx_id).field("Template").value())
            labels = str(self.xx_model.record(self.current_xx_id).field("Labels").value())

            template_list = eval(template)
            label_list = eval(labels)

            # turn self.param_value passed along with xx into a list of params
            param_value_list = self.getParamValueList()

            # assuming everything is ok (i.e., this xx actually has parameters), proceed
            if len(template_list) and len(label_list):
                # if somehow params come up short, create a blank set
                if not param_value_list or len(param_value_list) != len(template_list):
                    param_value_list = [""] * len(template_list)

                # **If it's not already there**, generate an entry in self.param_data_dict
                #  with one for each parameter to populate interface
                if name not in self.param_data_dict:
                    self.param_data_dict[name] = []
                    for i, x in enumerate(template_list):
                        type_item = x
                        param_item = label_list[i]

                        if name == initial_xx:
                            # first adding param passed, need to include passed value
                            v = self.getParamValueList()
                            value_item = v[i]
                        elif type_item in ("number",):  # note: varnum and obj_num are now names
                            value_item = 0
                        elif type_item in ("01float",):  # current primary use for volume so start at 1.0
                            value_item = 1.0
                        elif type_item in ("float",):
                            value_item = 0.0
                        elif type_item in ("fontsize",):  # current primary use for volume so start at 1.0
                            value_item = 14
                        elif type_item in ("bool",):
                            value_item = "False"
                        elif type_item in ("color",):
                            value_item = "['Black',0,0,0,255]"
                        elif type_item in ("fgcolor",):
                            value_item = "['Blue',0,0,255,255]"
                        elif type_item in ("bgcolor",):
                            value_item = "['White',255,255,255,255]"
                        else:
                            value_item = ""
                        self.param_data_dict[name].append([type_item, param_item, value_item])

            # create model
            self.xx_param_model = ParamListModel()

            if self.param_data_dict:
                self.xx_param_model.initData(self.param_data_dict, name, signal_update=self.signalUpdate)

            # attach model to view
            self.ui.xxparam_tableView.setModel(self.xx_param_model)

            # if there are parameters to edit, then let's make appropriate delegates
            if len(template_list) and len(label_list) and len(param_value_list):
                # create param editing delegate with different editors depending on param type
                delegate = genericrowdelegates.GenericRowDelegate()
                for i, x in enumerate(self.param_data_dict[name]):
                    type_item, param_item, value_item = x  # unpack components
                    if type_item == "number":
                        delegate.insertRowDelegate(i, genericrowdelegates.IntegerRowDelegate(0, 10000))
                    elif type_item == "fontsize":
                        font_size_list = [
                            "8",
                            "9",
                            "10",
                            "11",
                            "12",
                            "14",
                            "16",
                            "18",
                            "20",
                            "22",
                            "24",
                            "26",
                            "28",
                            "30",
                            "32",
                            "34",
                            "36",
                            "38",
                            "40",
                        ]
                        delegate.insertRowDelegate(i, genericrowdelegates.ComboRowDelegate(font_size_list))
                    elif type_item == "float":
                        delegate.insertRowDelegate(i, genericrowdelegates.FloatRowDelegate(0.0, 10000.0))
                    elif type_item == "01float":
                        delegate.insertRowDelegate(i, genericrowdelegates.FloatRowDelegate(0.0, 1.0))
                    elif type_item == "value":
                        delegate.insertRowDelegate(i, genericrowdelegates.PlainTextRowDelegate())
                    elif type_item == "richtext":
                        delegate.insertRowDelegate(i, genericrowdelegates.RichTextRowDelegate())
                    elif type_item == "viewnum":
                        delegate.insertRowDelegate(i, genericrowdelegates.ComboRowDelegate(self.view_list))
                    elif type_item == "objnum":
                        delegate.insertRowDelegate(i, genericrowdelegates.ComboRowDelegate(self.obj_list))
                    elif type_item == "key":
                        delegate.insertRowDelegate(i, genericrowdelegates.ComboRowDelegate(mykeys.keys))
                    elif type_item == "cursor":
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.ComboRowDelegate(mycursors.cursors),
                        )
                    elif "color" in type_item:
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.ComboRowColoredDelegate(self.color_list),
                        )
                    elif type_item == "bool":
                        onoff = ["False", "True"]
                        delegate.insertRowDelegate(i, genericrowdelegates.ComboRowDelegate(onoff))
                    elif type_item == "sndfile":
                        file_filter = "SoundFile (*.wav *.ogg *.mp3 *.wma *.au *.mp2 *.m4a)"
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.FileRowDelegate(self.media_path, file_filter),
                        )
                    elif type_item == "vidfile":
                        file_filter = "VideoFile (*.avi *.mov *.mp4 *.m4v *.ogg *.webm *.flv *.mpg *.mpeg *.wmv)"
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.FileRowDelegate(self.media_path, file_filter),
                        )
                    elif type_item == "exefile":
                        file_filter = "ProgramFile (*.exe *.app *.bat *.sh)"
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.FileRowDelegate(self.media_path, file_filter),
                        )
                    elif type_item == "picfile":
                        file_filter = "PictureFile (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)"
                        delegate.insertRowDelegate(
                            i,
                            genericrowdelegates.FileRowDelegate(self.media_path, file_filter),
                        )

                        # otherwise, should evoke default delegate

                # associated delegate with param table view
                self.ui.xxparam_tableView.setItemDelegate(delegate)

            # other table view config
            self.ui.xxparam_tableView.resizeColumnsToContents()
            self.ui.xxparam_tableView.resizeRowsToContents()

            # now that we have the name, look up and set the help_text
            self.ui.xxHelpLabel.setText(self.help_dict[name])

            # init the result string
            self.signalUpdate()

    def initializeXXModel(self, model, query):
        model.setQuery(query)
        # (Id INT, Name Text, Template Text, Labels Text )
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Id")
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "Name")
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, "Template")
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, "Labels")
        model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, "Restrictions")

    def connectXXModelToTableView(self, model, view):
        view.setModel(model)
        view.hideColumn(0)  # Id
        # view.hideColumn(1) #Name
        view.hideColumn(2)  # Template
        view.hideColumn(3)  # Labels
        view.hideColumn(4)  # Restrictions
        view.resizeColumnsToContents()

    def initializeDatabases(self):
        self.xx_model = CustomSqlModel()
        # note: (Id INT, Name Text, Template Text, Restrictions Text )
        if self.param_type == "Condition":
            xx_sql = f"select * from condition_lst where Restrictions like '%{self.action_type}%' order by Name;"
        elif self.param_type == "Trigger":
            xx_sql = f"select * from trigger_lst where Restrictions like '%{self.action_type}%' order by Name;"
        elif self.param_type == "Action":
            xx_sql = f"select * from action_lst where Restrictions like '%{self.action_type}%' order by Name;"
        else:
            log.error(f"Problem in initializeDatabases(), got bad coltype of {self.param_type}")
            return

        self.initializeXXModel(self.xx_model, xx_sql)
        self.connectXXModelToTableView(self.xx_model, self.ui.xx_tableView)

        selected = self.find_xx_data(self.param_string)
        if selected > -1:
            self.ui.xx_tableView.selectRow(selected)
            # now simulate clicking this so we can have the associated params already loaded
            self.current_xx_id = selected
            self.populateParamList()

        # setup selection model handler (mouse or keyboard)...have to do *after* table is filled: http://goo.gl/KPaajQ
        self.selection_model = self.ui.xx_tableView.selectionModel()
        self.selection_model.selectionChanged.connect(self.handleSelectionChange)

        self.xx_param_model = ParamListModel()
        # self.initializeXXParamModel(self.xx_param_model) # show nothing at start

    def setParamString(self, param_str):
        if self.current_xx_id is not None:
            self.param_string = param_str
            if self.param_string != "":
                self.populateParamList()

    def find_xx_data(self, data):
        p = str(data).find("(")
        if p > -1:
            dat = data[:p]
        else:
            dat = data
        dat = str(dat).lower()
        for r in range(self.xx_model.rowCount()):
            d = str(self.xx_model.record(r).field("Name").value()).lower()
            if d == dat:
                return r
        return -1

    def load_lists(self):
        view_names = {}
        query = QtSql.QSqlQuery()

        # Views
        query.exec("select Id, Name from views")
        if query.isActive():
            # while next(query):
            while query.next():
                view_id = query.value(0)  # id
                view_name = query.value(1)  # Name
                self.view_list.append(f"{view_id}:{view_name}")
                view_names[str(view_id)] = str(view_name)

        # Objects
        query.exec("select Id, Parent, Name from objects")
        if query.isActive():
            # while next(query):
            while query.next():
                object_id = query.value(0)
                parent_view_id = query.value(1)
                objname = query.value(2)
                parent_view_name = view_names[str(parent_view_id)]
                self.obj_list.append(f"{object_id}:{parent_view_name}:{objname}")

        # Colors
        self.color_list = []
        for color in mycolors.colors_large:
            self.color_list.append(f"['{str(color[0])}',{color[2][0]},{color[2][1]},{color[2][2]},255]")

    def setup_help_text(self):
        if self.param_type == "Condition":
            self.help_dict = helptext.condition_desc
        elif self.param_type == "Trigger":
            self.help_dict = helptext.trigger_desc
        elif self.param_type == "Action":
            self.help_dict = helptext.action_desc
