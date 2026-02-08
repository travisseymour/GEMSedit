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

from functools import partial
import os
from pathlib import Path
import platform
import subprocess
import time
import webbrowser

from PySide6 import QtCore, QtGui, QtSql, QtWidgets
from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QCloseEvent, QGuiApplication, QIcon
from PySide6.QtWidgets import QMessageBox

from gemsedit import LOG_PATH, app_long_name, log
from gemsedit.database import connection, gems_db, globalact
from gemsedit.database.sqltools import get_next_value
from gemsedit.gui import action_list
import gemsedit.gui.gems_window as win
from gemsedit.session import objects, settings
from gemsedit.session.networkgraph import show_gems_network_graph
from gemsedit.session.version import __version__
from gemsedit.utils.apputils import (
    get_resource,
    launch_in_terminal,
)


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


class ImageViewerDialog(QtWidgets.QDialog):
    """A simple modal dialog that displays a full-sized image and closes when clicked."""

    def __init__(self, image_path: str, view_name: str, image_type: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"GEMSedit: {view_name} {image_type} Picture. Click image to close.")
        self.setModal(True)

        # Load the image
        pixmap = QtGui.QPixmap(image_path)
        if pixmap.isNull():
            self.reject()
            return

        # Create a label to display the image
        self.image_label = QtWidgets.QLabel(self)
        self.image_label.setPixmap(pixmap)
        self.image_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Set up layout
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.image_label)

        # Size the dialog to fit the image (with some maximum constraints)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        max_width = int(screen.width() * 0.9)
        max_height = int(screen.height() * 0.9)

        if pixmap.width() > max_width or pixmap.height() > max_height:
            scaled_pixmap = pixmap.scaled(
                max_width,
                max_height,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)
            self.resize(scaled_pixmap.size())
        else:
            self.resize(pixmap.size())

    def mousePressEvent(self, event):
        """Close the dialog when clicked anywhere."""
        self.accept()


class GemsViews:
    MAX_RECENT_FILES = 10

    def __init__(self):
        self.connection = connection.GemsDB()
        self.model = None
        self.current_row = None
        self.basename = "View"
        self.base_table_name = "views"
        self.db_filename = ""
        self.media_path = ""
        self.object_win = None
        self.selection_model = None
        self.recent_menu = None

        self.MainWindow = QtWidgets.QMainWindow()
        self.MainWindow.setWindowIcon(QIcon(str(get_resource("images", "Icon.png"))))

        self.ui = win.Ui_ViewsWindow()
        self.ui.setupUi(self.MainWindow)

        self.settings = QSettings()
        self.prev_db_filename = self.settings.value("prev_db_filename", type=str, defaultValue="")
        self.gems_runner_path = self.settings.value("gems_runner_path", type=str, defaultValue="")
        self.recent_files = self.load_recent_files()

        log.info(f"GEMS_EDIT START v{__version__} ({time.strftime('%x')}-{time.strftime('%X')}).")

        self.MainWindow.network_window = None  # Optional[QWebEngineView]

        self.action_list = None
        self.task_action_editor = None
        self.task_config_editor = None

        self.connectSlots()
        self.disableButtons()

        self.center()
        self.setup_recent_menu()

        self.MainWindow.setWindowTitle(f"{app_long_name} version {__version__}")

        self.ui.actionSaveEnv.setIconVisibleInMenu(True)
        self.ui_timer = QTimer()
        self.ui_timer.timeout.connect(self.check_for_db_changed)
        self.ui_timer.start(1000)

    def center(self):
        qr = self.MainWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.MainWindow.move(qr.topLeft())

    def connectSlots(self):
        self.ui.view_tableView.doubleClicked.connect(self.handleBaseDoubleClick)
        self.ui.viewAdd_toolButton.pressed.connect(self.handleBaseAdd)
        self.ui.viewDel_toolButton.pressed.connect(self.handleBaseDel)
        self.ui.VAL_tableView.clicked.connect(self.handleActionClick)
        self.ui.objectsButton.pressed.connect(self.launchObjectsWindow)

        self.ui.actionTask_Actions.triggered.connect(self.launchTaskActionEditor)
        self.ui.actionTask_Configuration.triggered.connect(self.launchTaskConfigEditor)

        self.ui.fgDel_toolButton.pressed.connect(lambda: self.handlePicEdit("Foreground", mode="delete"))
        self.ui.bgDel_toolButton.pressed.connect(lambda: self.handlePicEdit("Background", mode="delete"))
        self.ui.olDel_toolButton.pressed.connect(lambda: self.handlePicEdit("Overlay", mode="delete"))

        self.ui.fgOpen_toolButton.pressed.connect(lambda: self.handlePicEdit("Foreground", mode="open"))
        self.ui.bgOpen_toolButton.pressed.connect(lambda: self.handlePicEdit("Background", mode="open"))
        self.ui.olOpen_toolButton.pressed.connect(lambda: self.handlePicEdit("Overlay", mode="open"))

        self.ui.fgCopy_toolButton.pressed.connect(lambda: self.handlePicEdit("Foreground", mode="copy"))
        self.ui.bgCopy_toolButton.pressed.connect(lambda: self.handlePicEdit("Background", mode="copy"))

        self.ui.actionNetwork_Graph.triggered.connect(self.handle_network_graph)
        self.ui.actionOpen.triggered.connect(self.open_environment)
        self.ui.actionClose.triggered.connect(self.closeEnv)
        self.ui.actionNew.triggered.connect(self.new_environment)
        self.ui.actionMedia.triggered.connect(self.launchMediaFolder)
        self.ui.actionRun_Environment.triggered.connect(self.runEnvironment)

        self.ui.actionLocate_GEMSrun.setVisible(False)
        # self.ui.actionLocate_GEMSrun.triggered.connect(self.locate_gemsrun)

        self.ui.actionSaveEnv.triggered.connect(self.handle_save_db)
        help_path = get_resource("docs", "gems_overview.pdf").resolve()
        help_url = help_path.as_uri()
        self.ui.actionDocumentation.triggered.connect(partial(webbrowser.open, help_url))

        self.MainWindow.closeEvent = self.main_window_close

        # Install event filters for picture label clicks
        self.fg_click_filter = ClickEventFilter(lambda: self.showBigPic("Foreground"))
        self.bg_click_filter = ClickEventFilter(lambda: self.showBigPic("Background"))
        self.ol_click_filter = ClickEventFilter(lambda: self.showBigPic("Overlay"))
        self.ui.fgPic_label.installEventFilter(self.fg_click_filter)
        self.ui.bgPic_label.installEventFilter(self.bg_click_filter)
        self.ui.olPic_label.installEventFilter(self.ol_click_filter)

        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def main_window_close(self, event: QCloseEvent) -> None:
        # close the db
        self.closeEnv()

        # save any settings that changed
        self.settings.setValue("prev_db_filename", self.prev_db_filename)
        self.settings.setValue("gems_runner_path", self.gems_runner_path)
        self.settings.setValue("recent_files", self.recent_files)

        # get out of here
        self.MainWindow.close()
        event.accept()

    # def locate_gemsrun_OLD_KEEP(self):
    #     # NOTE: We are no longer using this approach, because of our current
    #     #       reliance on PipX. However, we're KEEPING this code here in case
    #     #       we decide to switch back to a normal app+installer distribution approach
    #
    #     """try to automatically locate the GEMSrun application on various OS platforms"""
    #
    #     if sys.platform == "win32":  # same for 32 and 64bit windows.
    #         app_path = Path("C:", "Programs", "GEMSrun", "GEMSrun.exe")
    #         log.info(
    #             f"Searching for GEMSrun on Linux at {str(app_path)}..."
    #             f'{"Found!" if app_path.is_file() else "Not Found."}'
    #         )
    #         if not app_path.is_file():
    #             app_path = None
    #     elif sys.platform == "linux":
    #         app_path = Path("/", "opt", "GEMSrun", "GEMSrun")
    #         log.info(
    #             f"Searching for GEMSrun on Linux at {str(app_path)}..."
    #             f'{"Found!" if app_path.is_file() else "Not Found."}'
    #         )
    #         if not app_path.is_file():
    #             app_path = None
    #     elif sys.platform == "darwin":
    #         app_path = Path(
    #             "/", "Applications", "GEMSrun.app", "Contents", "Macos", "GEMSrun"
    #         )
    #         log.info(
    #             f"Searching for GEMSrun on Linux at {str(app_path)}..."
    #             f'{"Found!" if app_path.is_file() else "Not Found."}'
    #         )
    #         if not app_path.is_file():
    #             app_path = None
    #     else:
    #         log.error(
    #             f"You appear to be using an unsupported platform ({sys.platform}). "
    #             f"Contact developer to see if a suitable version of GEMSrun is available "
    #             f"for your operating system."
    #         )
    #         app_path = None
    #
    #     if app_path:
    #         self.gems_runner_path = str(app_path.resolve())
    #         _ = QMessageBox.information(
    #             self.MainWindow,
    #             "GEMSrun Found!",
    #             f"GEMSrun has been successfully located in {self.gems_runner_path}.\n"
    #             f"You should be able to run the current environment.",
    #             dialog_font,
    #         )
    #         return
    #
    #     # See if the user can find it
    #
    #     _ = QMessageBox.information(
    #         self.MainWindow,
    #         "GEMSrun Not Found.",
    #         f"GEMSrun could not be automatically located on your system. "
    #         f"On the next window, you will be asked to manually locate GEMSrun.",
    #         dialog_font,
    #     )
    #
    #     new_value = QtWidgets.QFileDialog.getOpenFileName(
    #         None, "Locate The GEMSrun Application", self.media_path
    #     )
    #     app_path = new_value[0]
    #
    #     # minimal check
    #
    #     if app_path and not Path(app_path).name.startswith("GEMSrun"):
    #         _ = QMessageBox.warning(
    #             self.MainWindow,
    #             "Unrecognized File",
    #             f'The selected file name "{Path(app_path).name}" does not appear to '
    #             f"be the GEMSrun application.",
    #             dialog_font,
    #         )
    #         app_path = ""
    #
    #     # set the global var
    #
    #     if app_path and Path(app_path).is_file():
    #         if sys.platform == "darwin" and Path(app_path).suffix == "app":
    #             app_path = Path(app_path, "Contents", "MacOS", "GEMSrun")
    #     else:
    #         app_path = ""
    #
    #     self.gems_runner_path = str(app_path)
    #     self.settings.setValue("gems_runner_path", self.gems_runner_path)

    # def runEnvironment_OLD_KEEP(self):
    #     """Runs current environment with GEMSrun, if it's installed and can be found."""
    #
    #     # NOTE: This approach is useful when GEMSrun is compiled to a normal
    #     #       executable and installed in the default system location.
    #     #       ***KEEP*** This here in case we decide to go back to this
    #     #       kind of distribution. For now, we'll use a different approach
    #     #       with PipX.
    #
    #     if self.db_filename:
    #         if not self.gems_runner_path or not Path(self.gems_runner_path).is_file():
    #             _ = QMessageBox.critical(
    #                 self.MainWindow,
    #                 "GEMSrun Application Not Found",
    #                 f"Unable to find GEMSrun application on your computer. "
    #                 f"Go to the RUN menu and click the LOCATE_GEMSRUN item.",
    #                 dialog_font,
    #             )
    #             return
    #
    #         gems_run = runlaunch.RunLaunch(self.db_filename)
    #         if gems_run.MainWindow.result():
    #             out = gems_run.outcome
    #             filename = Path(out["filename"])
    #             userid = out["userid"]
    #
    #             if not filename.is_file():
    #                 _ = QMessageBox.critical(
    #                     self.MainWindow,
    #                     "GEMSrun Error",
    #                     f"Environment file at {str(filename)} is not available or not readable.",
    #                     dialog_font,
    #                 )
    #                 return
    #
    #             cmd_parts = [
    #                 str(self.gems_runner_path),
    #                 "-f",
    #                 str(filename),
    #                 "-u",
    #                 str(userid),
    #             ]
    #             if not out["playmedia"]:
    #                 cmd_parts.append("--skipmedia")
    #             if not out["savedata"]:
    #                 cmd_parts.append("--skipdata")
    #             if out["debugging"]:
    #                 cmd_parts.append("--debug")
    #             cmd_parts.append("--skipgui")  # avoid the GEMSrun pop-up gui
    #
    #             try:
    #                 process = subprocess.Popen(cmd_parts, stdout=subprocess.PIPE)
    #                 output = [aline for aline in process.stdout]
    #                 process.wait()
    #                 # log.debug(f'RETURN CODE: {process.returncode}')
    #                 # log.debug(f'OUTPUT:\n{"\n".join(output)')
    #             except Exception as e:
    #                 _ = QMessageBox.critical(
    #                     self.MainWindow,
    #                     "GEMSrun Error",
    #                     f"Could not run environment, system gave this error message: {e}",
    #                     dialog_font,
    #                 )
    #
    #                 return

    def runEnvironment(self):
        """Runs current environment with GEMSrun, if it's installed and can be found."""

        if self.ui.actionSaveEnv.isEnabled():
            ret = QMessageBox.question(
                self.MainWindow,
                "Run Request With UnSaved Changes",
                "This environment has unsaved changes.\n"
                "OK: Run environment without current changes.\n"
                "SAVE: Save changes and then run the updated environment.\n"
                "CANCEL: Close this dialog window.",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )
            if ret == QtWidgets.QMessageBox.StandardButton.Cancel:
                return
            elif ret == QtWidgets.QMessageBox.StandardButton.Save:
                self.handle_save_db()
            elif ret == QtWidgets.QMessageBox.StandardButton.Ok:
                ...

        if self.db_filename:
            log.debug(f"Launching GEMSrun with {self.db_filename=}")

            try:
                launch_in_terminal("GEMSrun", params=["--file", self.db_filename])
            except Exception as e:
                _ = QMessageBox.critical(
                    self.MainWindow,
                    "GEMSrun Application Failed",
                    f'Attempting to run GEMSrun has failed with this error message:\n"{e}"',
                    QMessageBox.StandardButton.Ok,
                )
                return

    def check_for_db_changed(self):
        self.ui.actionSaveEnv.setEnabled(self.connection.db_opened() and connection.DB_CHANGED)

    def launchMediaFolder(self):
        if not self.media_path or not Path(self.media_path).is_dir():
            return

        try:
            system = platform.system()
            if system == "Windows":
                os.startfile(self.media_path)
            elif system == "Darwin":
                subprocess.run(["open", self.media_path], check=True)
            else:
                subprocess.run(["xdg-open", self.media_path], check=True)

        except Exception as e:
            log.error(f"Unable to open media folder in this location: {self.media_path}. ({e})")

    def launchTaskActionEditor(self):
        if self.model is not None:
            self.task_action_editor = globalact.GlobalAct(media_path=self.media_path, parent_win=self.MainWindow)
            self.MainWindow.hide()
            self.task_action_editor.MainWindow.show()

    def launchTaskConfigEditor(self):
        if self.model is not None:
            self.task_config_editor = settings.Settings(media_path=self.media_path, parent_win=self.MainWindow)
            self.MainWindow.hide()
            self.task_config_editor.MainWindow.show()

    def launchObjectsWindow(self):
        try:
            # FIXME: Why is this an issue?
            # For some reason this window gets called twice in a row.
            # This is a band-aid
            self.object_win.closeTheWindow()
        except:
            pass
        if self.current_row is not None:
            _id = self.model.record(self.current_row).value("Id")
            # pname = self.model.record(self.current_row).value("Name")
            fg_pic = self.model.record(self.current_row).value("Foreground")
            # bgpic = self.model.record(self.current_row).value("Background")
            if fg_pic == "":
                _ = QMessageBox.information(
                    self.MainWindow,
                    "Unable To Comply",
                    "First select a foreground picture for this view.",
                    QMessageBox.StandardButton.Ok,
                )
            else:
                self.object_win = objects.Objects(parentid=_id, mediapath=self.media_path, parent_win=self.MainWindow)
                self.object_win.MainWindow.setModal(False)
                self.MainWindow.move(self.MainWindow.pos().x(), self.MainWindow.pos().y())
                self.MainWindow.hide()
                self.object_win.MainWindow.show()
        else:
            _ = QMessageBox.information(
                self.MainWindow,
                "Unable To Comply",
                "Click on an existing view first.",
                QMessageBox.StandardButton.Ok,
            )

    def handle_network_graph(self):
        if self.connection.db_opened():
            show_gems_network_graph(parent=self.MainWindow, conn=self.connection, media_path=self.media_path)
        else:
            QMessageBox.information(
                self.MainWindow,
                "Network Graph Unavailable",
                "You must load or create an environment first.",
                QMessageBox.StandardButton.Ok,
            )

    def handle_save_db(self):
        self.connection.save_db()
        self.ui.actionSaveEnv.setEnabled(False)

    def handleActionClick(self, index):
        id = index.model().record(index.row()).value("Id")
        self.action_list.current_id = id

    def reinstateViewSelection(self, row=-1):
        # http://qt-project.org/doc/qt-4.8/model-view-programming.html#using-a-selection-model
        if row >= 0:
            curr_row = row
        else:
            curr_row = self.current_row
        if curr_row is not None and curr_row >= 0:
            curr_row_index = self.model.index(curr_row, 0, QtCore.QModelIndex())
            sel = QtCore.QItemSelection(curr_row_index, curr_row_index)
            self.selection_model.select(sel, QtCore.QItemSelectionModel.SelectionFlag.Select)
            self.ui.view_tableView.selectRow(curr_row)

    def handlePicEdit(self, field_name, mode):
        if self.db_filename == "" or field_name not in (
            "Foreground",
            "Background",
            "Overlay",
        ):
            return
        new_value = ""
        if mode == "copy":
            if field_name == "Foreground":
                new_value = Path(self.ui.bgPic_plainTextEdit.toPlainText()).name
            elif field_name == "Background":
                new_value = Path(self.ui.fgPic_plainTextEdit.toPlainText()).name
        elif mode == "delete":
            new_value = ""
        elif mode == "normal":
            if field_name == "Foreground":
                new_value = self.ui.fgPic_plainTextEdit.toPlainText()
            elif field_name == "Background":
                new_value = self.ui.bgPic_plainTextEdit.toPlainText()
            elif field_name == "Overlay":
                new_value = self.ui.olPic_plainTextEdit.toPlainText()
        elif mode == "open":
            filetype = "Images (*.png *.jpg *.jpeg *.bmp *.tif *.tiff *.gif *.webp)"
            new_value = QtWidgets.QFileDialog.getOpenFileName(
                None, "Select Image File", self.media_path, filter=filetype
            )
            new_value = Path(new_value[0]).name
            if new_value is None or new_value == "":
                return
        else:
            return

        _id = self.model.record(self.current_row).value("Id")
        query = QtSql.QSqlQuery()
        query.prepare(f"UPDATE {self.base_table_name} SET {field_name} = :newvalue WHERE Id = :id")
        query.bindValue(":newvalue", new_value)
        query.bindValue(":id", _id)
        query.exec()
        if query.lastError().isValid():
            log.error(f"Problem in handlePicEdit() update query: {query.lastError().text()}")

        self.model.setQuery("select * from " + self.base_table_name + " order by RowOrder")

        if mode != "normal":
            self.loadPicFields(skip_show_files=False)
        else:
            self.loadPicFields()

        self.reinstateViewSelection()

        connection.mark_db_as_changed()

    def clearPicFields(self):
        self.ui.fgPic_label.clear()
        self.ui.bgPic_label.clear()
        self.ui.olPic_label.clear()

        self.ui.fgPic_plainTextEdit.setPlainText("")
        self.ui.bgPic_plainTextEdit.setPlainText("")
        self.ui.olPic_plainTextEdit.setPlainText("")

    def loadPicFields(self, skip_show_files=True):
        self.clearPicFields()  # Either way clear first

        if self.current_row is None or self.model.rowCount() == 0:
            return

        # get the info from the model
        fg = os.path.join(self.media_path, self.model.record(self.current_row).value("Foreground"))
        bg = os.path.join(self.media_path, self.model.record(self.current_row).value("Background"))
        ol = os.path.join(self.media_path, self.model.record(self.current_row).value("Overlay"))

        # show filenames
        if not skip_show_files:
            if not os.path.isdir(fg):
                self.ui.fgPic_plainTextEdit.setPlainText(fg)
            if not os.path.isdir(bg):
                self.ui.bgPic_plainTextEdit.setPlainText(bg)
            if not os.path.isdir(ol):
                self.ui.olPic_plainTextEdit.setPlainText(ol)

        # load images
        if os.path.exists(fg):
            self.ui.fgPic_label.setPixmap(QtGui.QPixmap(fg))
            self.ui.fgPic_label.setScaledContents(True)
        else:
            self.ui.fgPic_label.clear()
        if os.path.exists(bg):
            self.ui.bgPic_label.setPixmap(QtGui.QPixmap(bg))
            self.ui.bgPic_label.setScaledContents(True)
        else:
            self.ui.bgPic_label.clear()
        if os.path.exists(ol):
            self.ui.olPic_label.setPixmap(QtGui.QPixmap(ol))
            self.ui.olPic_label.setScaledContents(True)
        else:
            self.ui.olPic_label.clear()

    # Note: connected to listview *after* list is filled from db
    def handleSelectionChange(self, selected, deselected):
        try:
            # get some required info
            selection = QtCore.QItemSelection(selected).indexes()[0]
            row = selection.row()
            _id = self.model.record(row).value("Id")

            # reflect change in ui
            self.current_row = row
            self.action_list.parent_id = _id

            self.action_list.filterActions()
            self.loadPicFields(False)

            obj_list = ""
            obj_count = 0
            query = QtSql.QSqlQuery()
            query.exec("select * from objects where Parent is {id} order by RowOrder")
            if query.isActive():
                while query.next():
                    obj_count += 1
                    obj_list += str(query.value(2)) + "\n"
                tooltip = f"Objects: {obj_count}\n--------\n{obj_list}"
                self.ui.objectsButton.setToolTip(tooltip)
                if obj_count > 0:
                    self.ui.objectsButton.setText("Objects")
                else:
                    self.ui.objectsButton.setText(f"Objects ({obj_count})")
            else:
                self.ui.objectsButton.setText("Objects")
        except Exception as e:
            log.error(f"Problem in handleSelectionChange({selected}, {deselected}): {e}")

    def handleBaseDoubleClick(self, index):
        id = index.model().record(index.row()).value("Id")
        name = index.model().record(index.row()).value("Name")
        self.editBaseName(id, name)

    def handleBaseAdd(self):
        bn = self.basename.title()
        new_id = get_next_value(column_name="Id", table_name=self.basename.lower() + "s", default=0)
        new_order = get_next_value(column_name="RowOrder", table_name=self.basename.lower() + "s", default=0)
        newname = f"New{bn}{new_id}"

        text = newname  # '???'
        ok = True
        while ok is True and str(text).isalnum() is False:
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                f"Adding New {bn}",
                f"Enter a(n) {bn} name (alpha numeric only, no spaces):",
            )
        if ok and str(text).isalnum():
            newname = str(text)

            query = QtSql.QSqlQuery()
            query.prepare(
                "INSERT INTO views (Id, Name, Foreground, Background, Overlay, RowOrder) "
                "VALUES (:id, :name, :fg, :bg, :ov, :ro)"
            )
            query.bindValue(":id", new_id)
            query.bindValue(":name", newname)
            query.bindValue(":fg", "")
            query.bindValue(":bg", "")
            query.bindValue(":ov", "")
            query.bindValue(":ro", new_order)
            query.exec()
            if query.lastError().isValid():
                log.error(f"Problem in handleBaseAdd(): {query.lastError().text()}")
            else:
                self.model.setQuery(f"select * from {self.base_table_name} order by RowOrder")
                if self.model.rowCount() > 0:
                    self.current_row = self.model.rowCount() - 1
                    self.ui.view_tableView.selectRow(self.current_row)
                    self.ui.view_tableView.scrollToBottom()
                    id = self.model.record(self.current_row).value("Id")
                    self.action_list.parent_id = id

                    # setup selection model handler (mouse or keyboard)...
                    # have to do *after* table is filled: http://goo.gl/KPaajQ
                    # NOTE: Testing..trying to get rid of misreferences in view list
                    # self.selectionmodel = self.ui.view_tableView.selectionModel()
                    # QtCore.QObject.connect(
                    #     self.selectionmodel,
                    #     QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                    #     self.handleSelectionChange
                    # )
                    # self.reinstateViewSelection(self.model.rowCount()-1)
                else:
                    self.action_list.parent_id = None
                    # QtCore.QObject.disconnect(self.selectionmodel,
                    #                           QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                    #                           self.handleSelectionChange)
                    self.selection_model.selectionChanged.disconnect()

                self.action_list.filterActions()
                self.loadPicFields()

            connection.mark_db_as_changed()

    def handleBaseDel(self):
        bn = self.basename.title()
        if self.current_row is not None:
            _id = self.model.record(self.current_row).value("Id")
            name = self.model.record(self.current_row).value("Name")
            # Make sure first

            ret = QMessageBox.question(
                self.MainWindow,
                f"Delete {bn} {name}",
                f"Really delete {name} and all of its associated actions?",
                QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Cancel,
            )

            if ret == QtWidgets.QMessageBox.StandardButton.Ok:
                error_list = []
                # delete base (view)
                query1 = QtSql.QSqlQuery()
                query1.prepare("DELETE FROM " + self.base_table_name + " where Id = :id")
                query1.bindValue(":id", _id)
                query1.exec()
                if query1.lastError().isValid():
                    log.error(f"Problem in handleBaseDel() deleting base: {query1.lastError().text()}")
                    error_list.append(1)
                # delete associated actions for base (view actions)
                query2 = QtSql.QSqlQuery()
                query2.prepare("DELETE FROM actions where ContextType = :actiontype and ContextId = :id")
                query2.bindValue(":actiontype", self.basename.lower())
                query2.bindValue(":id", _id)
                query2.exec()
                if query2.lastError().isValid():
                    log.error(f"Problem in handleBaseDel() deleting associated actions: {query2.lastError().text()}")
                    error_list.append(2)
                # delete actions associated with base (view) objects. yeah, really!
                # first get list of associated objects mama
                query3 = QtSql.QSqlQuery()
                query3.prepare("SELECT Id FROM objects WHERE Parent = :id")
                query3.bindValue(":id", _id)
                query3.exec()
                if query3.lastError().isValid():
                    log.error(f"Problem in handleBaseDel(): listing associated objects {query3.lastError().text()}")
                    error_list.append(3)
                else:
                    id_list = []
                    if query3.isActive():
                        while query3.next():
                            id_list.append(query3.value(0))
                    if id_list:
                        id_str_list = ",".join([str(n) for n in id_list])
                        id_str_list = "(" + id_str_list + ")"
                        # delete associated actions for base
                        query3 = QtSql.QSqlQuery()
                        query3.prepare(
                            f"DELETE FROM actions where ContextType = 'object' and ContextId in {id_str_list}"
                        )
                        query3.exec()
                        if query3.lastError().isValid():
                            log.error(
                                f"Problem in handleBaseDel(): deleting associated objects "
                                f"actions {query3.lastError().text()}"
                            )
                            error_list.append(3)
                # delete associated objects for base
                query4 = QtSql.QSqlQuery()
                query4.prepare("DELETE FROM objects where Parent = :id")
                query4.bindValue(":id", _id)
                query4.exec()
                if query4.lastError().isValid():
                    log.error(f"Problem in handleBaseDel(): deleting associated objects {query4.lastError().text()}")
                    error_list.append(4)
                # ok, refresh the display
                if not error_list:
                    self.model.setQuery("select * from " + self.base_table_name + " order by RowOrder")
                    if self.model.rowCount() > 0:
                        self.current_row = self.model.rowCount() - 1
                        self.ui.view_tableView.selectRow(self.current_row)
                        self.ui.view_tableView.scrollToBottom()
                        _id = self.model.record(self.current_row).value("Id")
                        self.action_list.parent_id = _id

                        # setup selection model handler (mouse or keyboard)...
                        # have to do *after* table is filled: http://goo.gl/KPaajQ
                        self.selection_model = self.ui.view_tableView.selectionModel()
                        # QtCore.QObject.connect(self.selectionmodel,
                        #                        QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                        #                        self.handleSelectionChange)
                        self.selection_model.selectionChanged.connect(self.handleSelectionChange)
                        if self.model.rowCount() > 0:
                            self.reinstateViewSelection(self.model.rowCount() - 1)
                    else:
                        self.action_list.parent_id = None
                        # QtCore.QObject.disconnect(self.selectionmodel,
                        #                           QtCore.SIGNAL("selectionChanged(QItemSelection,QItemSelection)"),
                        #                           self.handleSelectionChange)
                        self.selection_model.selectionChanged.connect(self.handleSelectionChange)
                    self.action_list.filterActions()
                    self.loadPicFields()

                connection.mark_db_as_changed()

    def editBaseName(self, _id, name):
        bn = self.basename.title()
        # get list of old names
        name_list = []
        query = QtSql.QSqlQuery()
        query.exec("select Name from " + self.base_table_name)
        if query.isActive():
            while query.next():
                name_list.append(query.value(0))
        if name in name_list:
            name_list.remove(name)
        # get the name
        new_name = "???"
        ok = True
        while ok is True and (str(new_name).isalnum() is False or str(new_name) in name_list):
            text, ok = QtWidgets.QInputDialog.getText(
                self.MainWindow,
                "Change " + bn + " Name",
                "Enter a " + bn.lower() + " name (alpha numeric only, no spaces):",
                text=name,
            )
            new_name = str(text)
            if new_name in name_list:
                ret = QMessageBox.question(
                    self.MainWindow,
                    "Duplicate Name Error",
                    f"{new_name} refers to an existing {bn.lower()}.\n"
                    f"You must choose a unique name for each {bn.lower()}.\n"
                    f"Press OK to try another name.",
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Cancel,
                )

                if ret == QtWidgets.QMessageBox.StandardButton.Cancel:
                    return
        if ok:
            # change name if it's actually different
            if new_name != name:
                query = QtSql.QSqlQuery()
                query.prepare("UPDATE " + self.base_table_name + " SET Name = :name WHERE Id = :id")
                query.bindValue(":id", _id)
                query.bindValue(":name", new_name)
                query.exec()
                if query.lastError().isValid():
                    log.error(f"Problem in editBaseName() update query: {query.lastError().text()}")
                else:
                    self.model.setQuery("select * from " + self.base_table_name + " order by RowOrder")

                connection.mark_db_as_changed()

    def initializeBaseModel(self, model, query):
        model.setQuery(query)
        # (Id INT, Name TEXT, Foreground BLOB, Background BLOB, Overlay BLOB)
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, "Id")
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, "Name")
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, "Foreground")
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, "Background")
        model.setHeaderData(4, QtCore.Qt.Orientation.Horizontal, "Overlay")
        model.setHeaderData(5, QtCore.Qt.Orientation.Horizontal, "RowOrder")

    def connectBaseModelToTableView(self, model, view):
        view.setModel(model)
        view.hideColumn(0)  # Id
        # view.hideColumn(1)  # ViewName
        view.hideColumn(2)  # Foreground
        view.hideColumn(3)  # Background
        view.hideColumn(4)  # Overlay
        view.hideColumn(5)  # RowOrder
        view.resizeColumnsToContents()

    def initializeDatabases(self):
        self.model = QtSql.QSqlQueryModel()
        self.initializeBaseModel(self.model, "select * from " + self.base_table_name + " order by RowOrder")
        self.connectBaseModelToTableView(self.model, self.ui.view_tableView)

    def initializeViews(self):
        # if there is anything in the base list, select the first one
        if self.model.rowCount() > 0:
            _id = self.model.record(0).value("Id")
            # select first row
            self.ui.view_tableView.selectRow(0)
            self.current_row = 0
            # load any corresponding actions
            self.action_list = action_list.ActionList(_id, self.ui.VAL_tableView, "view", media_path=self.media_path)
            self.action_list.parent_id = _id
            self.action_list.filterActions()
            # setup action_list buttons
            self.ui.actionAdd_toolButton.pressed.connect(self.action_list.handleActionAdd)
            self.ui.actionDel_toolButton.pressed.connect(self.action_list.handleActionDel)

            # handle pic fields
            self.loadPicFields(False)

            # setup selection model handler (mouse or keyboard)...
            # have to do *after* table is filled: http://goo.gl/KPaajQ
            self.selection_model = self.ui.view_tableView.selectionModel()
            self.selection_model.selectionChanged.connect(self.handleSelectionChange)

            # This clause just added to fix problem loading objects win when there are no objects
        else:
            self.action_list = action_list.ActionList(None, self.ui.view_tableView, "view", media_path=self.media_path)
            self.action_list.parent_id = None
            self.selection_model.selectionChanged.connect(self.handleSelectionChange)

    def new_environment(self):
        self.closeEnv()

        editor = QtWidgets.QFileDialog(self.MainWindow)
        filename, _ = editor.getSaveFileName(
            self.MainWindow,
            "Create GEMS environment file (???.yaml)",
            # str(Path(Path.home(), 'Desktop')),
            self.startDir(),
            "GEMS Environment Database (*.yaml)",
        )

        if not filename or len(filename) < 3:
            return

        file_path = Path(filename)
        file_path = Path(file_path.parent, file_path.stem.replace(" ", "_").strip() + ".yaml")
        media_folder = Path(file_path.parent, f"{file_path.stem}_media")

        errors = gems_db.new_database(yaml_db_file=file_path, media_folder=media_folder)

        if not errors:
            self.open_environment(str(file_path))
        else:
            err_msg = "\n".join(errors)
            QMessageBox.critical(
                self.MainWindow,
                "Database Error",
                f"Unable to create new GEMS environment:\n{err_msg}",
                QMessageBox.StandardButton.Ok,
            )

    def open_environment(self, file_name: str = ""):
        if not file_name:
            editor = QtWidgets.QFileDialog(self.MainWindow)
            editor.setFileMode(QtWidgets.QFileDialog.FileMode.ExistingFile)
            filename, _ = editor.getOpenFileName(
                self.MainWindow,
                "Choose an existing GEMS environment file (*.yaml)",
                # str(Path(Path.home(), 'Desktop')),
                self.startDir(),
                "GEMS Environment Database (*.yaml)",
            )
            if not filename:
                return
        else:
            filename = file_name

        if not filename.lower().endswith(".yaml"):
            QMessageBox.critical(
                self.MainWindow,
                "Filename Error",
                "File doesn't appear to be a GEMS Environment file, filename doesn't end with '*.yaml':\n{filename}",
                QMessageBox.StandardButton.Ok,
            )
            return

        if not Path(filename).is_file():
            if file_name:
                self.remove_recent_file(file_name)
            QMessageBox.critical(
                self.MainWindow,
                "Filename Error",
                f"Unable to load this file:\n{filename}",
                QMessageBox.StandardButton.Ok,
            )
            return

        chosen_file_path = Path(filename)
        project_root = chosen_file_path.parent
        project_name = chosen_file_path.stem.replace(" ", "_").strip()
        project_media_folder = Path(project_root, f"{project_name}_media")

        if not project_media_folder.is_dir():
            if (
                self.askYesNo(
                    "Create Media Folder?",
                    f"GEMS expects a media folder in the same one where "
                    f"the environment file was found. In particular, the "
                    f"folder {str(project_media_folder)} appears to be missing. GEMS requires that "
                    f"all media be placed in this folder. Would you like"
                    f"to create it now?",
                )
                is True
            ):
                try:
                    project_media_folder.mkdir(exist_ok=True)
                except:
                    QMessageBox.critical(
                        self.MainWindow,
                        "Filesystem Error",
                        f"Unable to create media folder {str(project_media_folder)}. "
                        f"You will need to manually create this folder"
                        f"in order to run GEMS.",
                        QMessageBox.StandardButton.Ok,
                    )
                    return
            else:
                return

        self.media_path = str(project_media_folder)

        ui_db_tables_file = get_resource("UiDBTables.yaml")

        if self.connection.open_db(db_yaml_file=filename, ui_list_yaml_file=ui_db_tables_file):
            self.db_filename = filename
            self.add_recent_file(filename)
            self.initializeDatabases()
            self.initializeViews()
            self.ui.dbfilename_Label.setText(os.path.basename(filename))
            self.enableButtons()
        else:
            QMessageBox.critical(
                self.MainWindow,
                "Database Error",
                f"Database Error While Loading GEMS Environment file:\n{filename}",
                QMessageBox.StandardButton.Ok,
            )

        log.debug(f"{self.db_filename=}")

    def closeEnv(self):
        if self.connection.db_opened():
            self.connection.close_db(offer_to_save_changes=connection.DB_CHANGED)

        self.model = None
        self.current_row = None
        self.prev_db_filename = self.db_filename
        self.db_filename = ""
        self.media_path = ""

        self.ui.dbfilename_Label.setText("...")

        self.ui.fgPic_plainTextEdit.setPlainText("")
        self.ui.bgPic_plainTextEdit.setPlainText("")
        self.ui.olPic_plainTextEdit.setPlainText("")

        self.ui.fgPic_label.clear()
        self.ui.bgPic_label.clear()
        self.ui.olPic_label.clear()

        self.ui.view_tableView.setModel(None)
        self.ui.VAL_tableView.setModel(None)

        self.disableButtons()

    def startDir(self):
        if os.path.exists(self.db_filename) is True:
            return os.path.dirname(self.db_filename)
        elif os.path.exists(os.path.dirname(self.prev_db_filename)) is True:
            return os.path.dirname(self.prev_db_filename)
        else:
            return os.getcwd()

    def showBigPic(self, image_type: str):
        if self.db_filename == "" or self.current_row is None:
            return

        # Get the image filename from the appropriate text field
        if image_type == "Foreground":
            image_filename = self.ui.fgPic_plainTextEdit.toPlainText()
        elif image_type == "Background":
            image_filename = self.ui.bgPic_plainTextEdit.toPlainText()
        elif image_type == "Overlay":
            image_filename = self.ui.olPic_plainTextEdit.toPlainText()
        else:
            return

        if not image_filename:
            return

        # Construct full path
        image_path = os.path.join(self.media_path, image_filename)
        if not os.path.exists(image_path):
            return

        # Get view name for the title
        view_name = self.model.record(self.current_row).value("Name")

        # Show the image viewer dialog
        dialog = ImageViewerDialog(image_path, view_name, image_type, self.MainWindow)
        dialog.exec()

    def enableButtons(self):
        self.ui.actionAdd_toolButton.setEnabled(True)
        self.ui.actionDel_toolButton.setEnabled(True)
        self.ui.bgDel_toolButton.setEnabled(True)
        self.ui.bgOpen_toolButton.setEnabled(True)
        self.ui.fgDel_toolButton.setEnabled(True)
        self.ui.fgOpen_toolButton.setEnabled(True)
        self.ui.olDel_toolButton.setEnabled(True)
        self.ui.olOpen_toolButton.setEnabled(True)
        self.ui.viewAdd_toolButton.setEnabled(True)
        self.ui.viewDel_toolButton.setEnabled(True)
        self.ui.fgCopy_toolButton.setEnabled(True)
        self.ui.bgCopy_toolButton.setEnabled(True)

    def disableButtons(self):
        self.ui.actionAdd_toolButton.setEnabled(False)
        self.ui.actionDel_toolButton.setEnabled(False)
        self.ui.bgDel_toolButton.setEnabled(False)
        self.ui.bgOpen_toolButton.setEnabled(False)
        self.ui.fgDel_toolButton.setEnabled(False)
        self.ui.fgOpen_toolButton.setEnabled(False)
        self.ui.olDel_toolButton.setEnabled(False)
        self.ui.olOpen_toolButton.setEnabled(False)
        self.ui.viewAdd_toolButton.setEnabled(False)
        self.ui.viewDel_toolButton.setEnabled(False)
        self.ui.fgCopy_toolButton.setEnabled(False)
        self.ui.bgCopy_toolButton.setEnabled(False)

    def askOKCancel(self, text: str, info_text: str) -> bool:
        ret = QMessageBox.question(
            self.MainWindow,
            text,
            info_text,
            QtWidgets.QMessageBox.StandardButton.Cancel | QtWidgets.QMessageBox.StandardButton.Ok,
            QtWidgets.QMessageBox.StandardButton.Cancel,
        )

        if ret == QtWidgets.QMessageBox.StandardButton.Ok:
            return True
        else:
            return False

    def askYesNo(self, text: str, info_text: str) -> bool:
        ret = QMessageBox.question(
            self.MainWindow,
            text,
            info_text,
            QtWidgets.QMessageBox.StandardButton.No | QtWidgets.QMessageBox.StandardButton.Yes,
            QtWidgets.QMessageBox.StandardButton.No,
        )

        if ret == QtWidgets.QMessageBox.StandardButton.Yes:
            return True
        else:
            return False

    def load_recent_files(self) -> list[str]:
        files = self.settings.value("recent_files", defaultValue=[], type=list)
        if not isinstance(files, list):
            return []
        return [str(Path(f)) for f in files if f]

    def setup_recent_menu(self) -> None:
        self.recent_menu = QtWidgets.QMenu("Open Recent", self.MainWindow)
        self.ui.menuFile.insertMenu(self.ui.actionClose, self.recent_menu)
        self.recent_menu.aboutToShow.connect(self.update_recent_menu)
        self.update_recent_menu()

    def update_recent_menu(self) -> None:
        if not self.recent_menu:
            return

        self.recent_menu.clear()
        self.recent_files = [p for p in self.recent_files if Path(p).is_file()]
        self.settings.setValue("recent_files", self.recent_files)

        if not self.recent_files:
            action = self.recent_menu.addAction("No recent files")
            action.setEnabled(False)
            return

        for path in self.recent_files[: self.MAX_RECENT_FILES]:
            label = self.format_recent_label(path)
            action = self.recent_menu.addAction(label)
            action.triggered.connect(partial(self.open_environment, path))

        self.recent_menu.addSeparator()
        clear_action = self.recent_menu.addAction("Clear Items")
        clear_action.triggered.connect(self.clear_recent_files)

    def add_recent_file(self, filename: str) -> None:
        normalized = str(Path(filename).resolve())

        if normalized in self.recent_files:
            self.recent_files.remove(normalized)

        self.recent_files.insert(0, normalized)
        self.recent_files = self.recent_files[: self.MAX_RECENT_FILES]

        self.settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def clear_recent_files(self) -> None:
        self.recent_files = []
        self.settings.setValue("recent_files", self.recent_files)
        self.update_recent_menu()

    def remove_recent_file(self, filename: str) -> None:
        normalized = str(Path(filename).resolve())
        if normalized in self.recent_files:
            self.recent_files.remove(normalized)
            self.settings.setValue("recent_files", self.recent_files)
            self.update_recent_menu()

    def format_recent_label(self, path: str) -> str:
        try:
            expanded = str(Path(path).resolve())
            home = str(Path.home())
            if expanded.startswith(home):
                return expanded.replace(home, "~", 1)
            return expanded
        except Exception:
            return path
