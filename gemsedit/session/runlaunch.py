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

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QMessageBox

import gemsedit.gui.run_launch_dlg as win
from PySide6 import QtCore, QtWidgets
import os


class RunLaunch:
    def __init__(self, filename, editfile=False, defaultdir="/"):
        self.MainWindow = QtWidgets.QDialog()
        self.ui = win.Ui_GEMSRunDialog()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.setModal(True)

        self.overwriteGroup = QtWidgets.QButtonGroup()
        self.overwriteGroup.addButton(self.ui.overwrite_radioButton, 1)
        self.overwriteGroup.addButton(self.ui.rename_radioButton, 2)

        self.filename = filename
        self.editfile = editfile
        self.defaultdir = defaultdir
        self.userid = ""
        self.savedata = True
        self.overwrite = False
        self.playmedia = True
        self.debugging = False
        self.outcome = {}
        self.ui.fileselect_toolButton.setEnabled(self.editfile)

        self.connectSlots()
        self.setupUiData()

        self.center()

        self.MainWindow.exec()

    def center(self):
        qr = self.MainWindow.frameGeometry()
        cp = QGuiApplication.primaryScreen().availableGeometry().center()
        qr.moveCenter(cp)
        self.MainWindow.move(qr.topLeft())

    def setupUiData(self):
        if self.ui.user_plainTextEdit.toPlainText() == "":
            self.ui.user_plainTextEdit.setPlainText("User1")
        self.ui.dbfile_plainTextEdit.setPlainText(self.filename)

    def updateFN(self):
        self.ui.filename_label.setText(
            "Data Filename: gemsrun_%s.txt" % self.ui.user_plainTextEdit.toPlainText().strip()
        )
        self.userid = self.ui.user_plainTextEdit.toPlainText().strip()

    def updateSAVE(self, b):
        self.savedata = b

    def updateOverwrite(self, i):
        if i == 1:
            self.overwrite = True
        else:
            self.overwrite = False

    def updateSkipmedia(self, b):
        self.playmedia = b

    def updateDebug(self, b):
        self.debugging = b

    def connectSlots(self):
        # QtCore.QObject.connect(self.ui.run_pushButton, QtCore.SIGNAL("pressed()"), self.launchRunner)
        # QtCore.QObject.connect(self.ui.user_plainTextEdit, QtCore.SIGNAL("textChanged()"), self.updateFN)
        # QtCore.QObject.connect(self.ui.save_checkBox, QtCore.SIGNAL("toggled(bool)"), self.updateSAVE)
        # QtCore.QObject.connect(self.overwriteGroup, QtCore.SIGNAL("buttonPressed(int)"), self.updateOverwrite)
        # QtCore.QObject.connect(self.ui.media_checkBox, QtCore.SIGNAL("toggled(bool)"), self.updateSkipmedia)
        # QtCore.QObject.connect(self.ui.debug_checkBox, QtCore.SIGNAL("toggled(bool)"), self.updateDebug)

        self.ui.run_pushButton.pressed.connect(self.launchRunner)
        self.ui.user_plainTextEdit.textChanged.connect(self.updateFN)
        self.ui.save_checkBox.toggled.connect(self.updateSAVE)
        self.overwriteGroup.buttonPressed.connect(self.updateOverwrite)
        self.ui.media_checkBox.toggled.connect(self.updateSkipmedia)
        self.ui.debug_checkBox.toggled.connect(self.updateDebug)

        # QtCore.QObject.connect(self.ui.fileselect_toolButton, QtCore.SIGNAL("pressed()"), self.selectDBFile)
        self.ui.fileselect_toolButton.pressed.connect(self.selectDBFile)
        QtCore.QMetaObject.connectSlotsByName(self.MainWindow)

    def selectDBFile(self):
        fname, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Environment DB File", self.defaultdir)
        if fname:
            if os.path.exists(fname) and os.path.isfile(fname):
                self.ui.dbfile_plainTextEdit.setPlainText(fname)
                self.filename = fname
            else:
                _ = QMessageBox.critical(
                    None,
                    "File Access Error!",
                    "Unable to access the selected file. Please close this dialog and select another file.",
                    QMessageBox.StandardButton.Ok,
                )

    def launchRunner(self):
        self.outcome = {
            "filename": self.filename,
            "userid": self.userid,
            "savedata": self.savedata,
            "overwrite": self.overwrite,
            "playmedia": self.playmedia,
            "debugging": self.debugging,
        }
        self.MainWindow.accept()
