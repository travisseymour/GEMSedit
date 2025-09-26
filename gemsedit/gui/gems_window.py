# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'gems_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt
from PySide6.QtGui import QAction, QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QGridLayout,
    QLabel,
    QLayout,
    QMenu,
    QMenuBar,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTabWidget,
    QTableView,
    QToolBar,
    QToolButton,
    QWidget,
)
import gemsedit.gui.gemsedit_rc  # noqa: F401

from gemsedit.gui.CustomClickableLabel import ClickableLabel


class Ui_ViewsWindow(object):
    def setupUi(self, ViewsWindow):
        if not ViewsWindow.objectName():
            ViewsWindow.setObjectName("ViewsWindow")
        ViewsWindow.resize(1400, 800)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(ViewsWindow.sizePolicy().hasHeightForWidth())
        ViewsWindow.setSizePolicy(sizePolicy)
        ViewsWindow.setMinimumSize(QSize(0, 0))
        ViewsWindow.setMaximumSize(QSize(16777215, 16777215))
        font = QFont()
        font.setFamilies(["Verdana"])
        font.setPointSize(12)
        ViewsWindow.setFont(font)
        ViewsWindow.setTabShape(QTabWidget.Rounded)
        self.actionOpen = QAction(ViewsWindow)
        self.actionOpen.setObjectName("actionOpen")
        icon = QIcon()
        icon.addFile(":/newPrefix/media/1409888970_Folder.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionOpen.setIcon(icon)
        font1 = QFont()
        font1.setPointSize(12)
        self.actionOpen.setFont(font1)
        self.actionNew = QAction(ViewsWindow)
        self.actionNew.setObjectName("actionNew")
        icon1 = QIcon()
        icon1.addFile(":/newPrefix/media/add-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionNew.setIcon(icon1)
        self.actionNew.setFont(font1)
        self.actionClose = QAction(ViewsWindow)
        self.actionClose.setObjectName("actionClose")
        icon2 = QIcon()
        icon2.addFile(":/newPrefix/media/1409889639_Cancel.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionClose.setIcon(icon2)
        self.actionClose.setFont(font1)
        self.actionQuit = QAction(ViewsWindow)
        self.actionQuit.setObjectName("actionQuit")
        icon3 = QIcon()
        icon3.addFile(":/newPrefix/media/1409888938_Log Out.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionQuit.setIcon(icon3)
        self.actionQuit.setFont(font1)
        self.actionTask_Configuration = QAction(ViewsWindow)
        self.actionTask_Configuration.setObjectName("actionTask_Configuration")
        icon4 = QIcon()
        icon4.addFile(":/newPrefix/media/1409888901_Settings.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionTask_Configuration.setIcon(icon4)
        self.actionTask_Configuration.setFont(font1)
        self.actionTask_Actions = QAction(ViewsWindow)
        self.actionTask_Actions.setObjectName("actionTask_Actions")
        icon5 = QIcon()
        icon5.addFile(":/newPrefix/media/1409889836_Properties.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionTask_Actions.setIcon(icon5)
        self.actionTask_Actions.setFont(font1)
        self.actionDocumentation = QAction(ViewsWindow)
        self.actionDocumentation.setObjectName("actionDocumentation")
        icon6 = QIcon()
        icon6.addFile(":/newPrefix/media/1409889623_Help.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionDocumentation.setIcon(icon6)
        self.actionDocumentation.setFont(font1)
        self.actionRun_Environment = QAction(ViewsWindow)
        self.actionRun_Environment.setObjectName("actionRun_Environment")
        icon7 = QIcon()
        icon7.addFile(":/newPrefix/media/1409971621_Play.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionRun_Environment.setIcon(icon7)
        self.actionRun_Environment.setFont(font1)
        self.actionMedia = QAction(ViewsWindow)
        self.actionMedia.setObjectName("actionMedia")
        icon8 = QIcon()
        icon8.addFile(":/newPrefix/media/folder-images-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionMedia.setIcon(icon8)
        self.actionMedia.setFont(font1)
        self.actionLocate_GEMSrun = QAction(ViewsWindow)
        self.actionLocate_GEMSrun.setObjectName("actionLocate_GEMSrun")
        self.actionLocate_GEMSrun.setEnabled(False)
        self.actionLocate_GEMSrun.setFont(font1)
        self.actionSave = QAction(ViewsWindow)
        self.actionSave.setObjectName("actionSave")
        self.actionSave.setEnabled(False)
        icon9 = QIcon()
        icon9.addFile(":/newPrefix/media/Save-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionSave.setIcon(icon9)
        self.actionSaveEnv = QAction(ViewsWindow)
        self.actionSaveEnv.setObjectName("actionSaveEnv")
        self.actionSaveEnv.setEnabled(True)
        self.actionSaveEnv.setIcon(icon9)
        self.actionNetwork_Graph = QAction(ViewsWindow)
        self.actionNetwork_Graph.setObjectName("actionNetwork_Graph")
        icon10 = QIcon()
        icon10.addFile(":/newPrefix/media/network_color.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.actionNetwork_Graph.setIcon(icon10)
        self.actionNetwork_Graph.setFont(font1)
        self.centralwidget = QWidget(ViewsWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.tabWidget.sizePolicy().hasHeightForWidth())
        self.tabWidget.setSizePolicy(sizePolicy1)
        self.tabWidget.setMinimumSize(QSize(1114, 679))
        self.tabWidget.setBaseSize(QSize(1114, 679))
        self.tabWidget.setFont(font)
        self.tabWidget.setAutoFillBackground(False)
        self.tabWidget.setDocumentMode(True)
        self.maintab = QWidget()
        self.maintab.setObjectName("maintab")
        self.gridLayout_10 = QGridLayout(self.maintab)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.splitter_2 = QSplitter(self.maintab)
        self.splitter_2.setObjectName("splitter_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.splitter_2.sizePolicy().hasHeightForWidth())
        self.splitter_2.setSizePolicy(sizePolicy2)
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.splitter_2.setHandleWidth(7)
        self.layoutWidget = QWidget(self.splitter_2)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_3 = QGridLayout(self.layoutWidget)
        self.gridLayout_3.setSpacing(6)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.gridLayout_3.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        font2 = QFont()
        font2.setFamilies(["Verdana"])
        font2.setPointSize(16)
        font2.setItalic(False)
        self.label_4.setFont(font2)
        self.label_4.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        self.label_6.setMaximumSize(QSize(50, 50))
        self.label_6.setPixmap(QPixmap(":/newPrefix/media/Antialiasfactory-Jewelry-Agate.ico"))
        self.label_6.setScaledContents(True)

        self.gridLayout_3.addWidget(self.label_6, 0, 3, 1, 2)

        self.viewDel_toolButton = QToolButton(self.layoutWidget)
        self.viewDel_toolButton.setObjectName("viewDel_toolButton")
        icon11 = QIcon()
        icon11.addFile(":/newPrefix/media/delete-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.viewDel_toolButton.setIcon(icon11)

        self.gridLayout_3.addWidget(self.viewDel_toolButton, 1, 4, 1, 1)

        self.viewAdd_toolButton = QToolButton(self.layoutWidget)
        self.viewAdd_toolButton.setObjectName("viewAdd_toolButton")
        self.viewAdd_toolButton.setIcon(icon1)

        self.gridLayout_3.addWidget(self.viewAdd_toolButton, 1, 3, 1, 1)

        self.labelAppName = QLabel(self.layoutWidget)
        self.labelAppName.setObjectName("labelAppName")
        font3 = QFont()
        font3.setFamilies(["Verdana"])
        font3.setPointSize(24)
        font3.setBold(True)
        self.labelAppName.setFont(font3)

        self.gridLayout_3.addWidget(self.labelAppName, 0, 0, 1, 2)

        self.view_tableView = QTableView(self.layoutWidget)
        self.view_tableView.setObjectName("view_tableView")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.view_tableView.sizePolicy().hasHeightForWidth())
        self.view_tableView.setSizePolicy(sizePolicy3)
        self.view_tableView.setMaximumSize(QSize(16777215, 16777215))
        self.view_tableView.setBaseSize(QSize(276, 532))
        font4 = QFont()
        font4.setFamilies(["Verdana"])
        font4.setPointSize(14)
        font4.setBold(True)
        self.view_tableView.setFont(font4)
        self.view_tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.view_tableView.setDragEnabled(True)
        self.view_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.view_tableView.setAlternatingRowColors(True)
        self.view_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.view_tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.view_tableView.horizontalHeader().setVisible(False)
        self.view_tableView.horizontalHeader().setStretchLastSection(True)
        self.view_tableView.verticalHeader().setVisible(False)

        self.gridLayout_3.addWidget(self.view_tableView, 2, 0, 1, 5)

        self.horizontalSpacer_6 = QSpacerItem(90, 28, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer_6, 1, 1, 1, 2)

        self.horizontalSpacer = QSpacerItem(18, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_3.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.splitter_2.addWidget(self.layoutWidget)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName("splitter")
        sizePolicy2.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy2)
        self.splitter.setOrientation(Qt.Vertical)
        self.splitter.setHandleWidth(7)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.gridLayout_5 = QGridLayout(self.layoutWidget1)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.gridLayout_5.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QLabel(self.layoutWidget1)
        self.label.setObjectName("label")
        font5 = QFont()
        font5.setFamilies(["Verdana"])
        font5.setPointSize(12)
        font5.setBold(True)
        font5.setItalic(False)
        self.label.setFont(font5)

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.dbfilename_Label = QLabel(self.layoutWidget1)
        self.dbfilename_Label.setObjectName("dbfilename_Label")
        self.dbfilename_Label.setFont(font)

        self.gridLayout.addWidget(self.dbfilename_Label, 0, 1, 1, 1)

        self.horizontalSpacer_2 = QSpacerItem(268, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer_2, 0, 2, 1, 1)

        self.objectsButton = QPushButton(self.layoutWidget1)
        self.objectsButton.setObjectName("objectsButton")
        self.objectsButton.setFont(font2)

        self.gridLayout.addWidget(self.objectsButton, 0, 3, 1, 1)

        self.gridLayout_5.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.gridLayout_4 = QGridLayout()
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.label_3.setFont(font2)
        self.label_3.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.gridLayout_4.addWidget(self.label_3, 0, 0, 1, 1)

        self.horizontalSpacer_4 = QSpacerItem(538, 28, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_4.addItem(self.horizontalSpacer_4, 0, 1, 1, 1)

        self.actionAdd_toolButton = QToolButton(self.layoutWidget1)
        self.actionAdd_toolButton.setObjectName("actionAdd_toolButton")
        self.actionAdd_toolButton.setIcon(icon1)

        self.gridLayout_4.addWidget(self.actionAdd_toolButton, 0, 2, 1, 1)

        self.actionDel_toolButton = QToolButton(self.layoutWidget1)
        self.actionDel_toolButton.setObjectName("actionDel_toolButton")
        self.actionDel_toolButton.setIcon(icon11)

        self.gridLayout_4.addWidget(self.actionDel_toolButton, 0, 3, 1, 1)

        self.VAL_tableView = QTableView(self.layoutWidget1)
        self.VAL_tableView.setObjectName("VAL_tableView")
        self.VAL_tableView.setMinimumSize(QSize(622, 192))
        self.VAL_tableView.setFont(font)
        self.VAL_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.VAL_tableView.setDragEnabled(True)
        self.VAL_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.VAL_tableView.setAlternatingRowColors(True)
        self.VAL_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.VAL_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.VAL_tableView.horizontalHeader().setStretchLastSection(True)
        self.VAL_tableView.verticalHeader().setVisible(False)

        self.gridLayout_4.addWidget(self.VAL_tableView, 1, 0, 1, 4)

        self.gridLayout_5.addLayout(self.gridLayout_4, 1, 0, 1, 1)

        self.splitter.addWidget(self.layoutWidget1)
        self.layoutWidget2 = QWidget(self.splitter)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.gridLayout_9 = QGridLayout(self.layoutWidget2)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout_9.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_7 = QLabel(self.layoutWidget2)
        self.label_7.setObjectName("label_7")
        self.label_7.setMaximumSize(QSize(16777215, 28))
        font6 = QFont()
        font6.setFamilies(["Verdana"])
        font6.setPointSize(14)
        font6.setBold(False)
        font6.setItalic(False)
        self.label_7.setFont(font6)
        self.label_7.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_7.setAlignment(Qt.AlignCenter)

        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)

        self.fgOpen_toolButton = QToolButton(self.layoutWidget2)
        self.fgOpen_toolButton.setObjectName("fgOpen_toolButton")
        icon12 = QIcon()
        icon12.addFile(":/newPrefix/media/folder-open-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.fgOpen_toolButton.setIcon(icon12)

        self.gridLayout_6.addWidget(self.fgOpen_toolButton, 0, 1, 1, 1)

        self.fgCopy_toolButton = QToolButton(self.layoutWidget2)
        self.fgCopy_toolButton.setObjectName("fgCopy_toolButton")
        icon13 = QIcon()
        icon13.addFile(
            ":/newPrefix/media/1409970886_circle-arrow-left-48.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.fgCopy_toolButton.setIcon(icon13)

        self.gridLayout_6.addWidget(self.fgCopy_toolButton, 0, 2, 1, 1)

        self.fgDel_toolButton = QToolButton(self.layoutWidget2)
        self.fgDel_toolButton.setObjectName("fgDel_toolButton")
        self.fgDel_toolButton.setIcon(icon11)

        self.gridLayout_6.addWidget(self.fgDel_toolButton, 0, 3, 1, 1)

        self.fgPic_plainTextEdit = QPlainTextEdit(self.layoutWidget2)
        self.fgPic_plainTextEdit.setObjectName("fgPic_plainTextEdit")
        self.fgPic_plainTextEdit.setMinimumSize(QSize(285, 0))
        self.fgPic_plainTextEdit.setMaximumSize(QSize(16777215, 60))
        self.fgPic_plainTextEdit.setFont(font)
        self.fgPic_plainTextEdit.setReadOnly(True)

        self.gridLayout_6.addWidget(self.fgPic_plainTextEdit, 1, 0, 1, 4)

        self.fgPic_label = ClickableLabel(self.layoutWidget2)
        self.fgPic_label.setObjectName("fgPic_label")
        self.fgPic_label.setMinimumSize(QSize(259, 239))
        self.fgPic_label.setMaximumSize(QSize(16777215, 16777215))
        self.fgPic_label.setFont(font)
        self.fgPic_label.setFrameShape(QFrame.Box)

        self.gridLayout_6.addWidget(self.fgPic_label, 2, 0, 1, 4)

        self.gridLayout_9.addLayout(self.gridLayout_6, 0, 0, 1, 1)

        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_8 = QLabel(self.layoutWidget2)
        self.label_8.setObjectName("label_8")
        self.label_8.setMaximumSize(QSize(16777215, 28))
        self.label_8.setFont(font6)
        self.label_8.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_8.setAlignment(Qt.AlignCenter)

        self.gridLayout_7.addWidget(self.label_8, 0, 0, 1, 1)

        self.bgOpen_toolButton = QToolButton(self.layoutWidget2)
        self.bgOpen_toolButton.setObjectName("bgOpen_toolButton")
        self.bgOpen_toolButton.setIcon(icon12)

        self.gridLayout_7.addWidget(self.bgOpen_toolButton, 0, 1, 1, 1)

        self.bgCopy_toolButton = QToolButton(self.layoutWidget2)
        self.bgCopy_toolButton.setObjectName("bgCopy_toolButton")
        icon14 = QIcon()
        icon14.addFile(
            ":/newPrefix/media/1409970876_circle-arrow-right-48.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off
        )
        self.bgCopy_toolButton.setIcon(icon14)

        self.gridLayout_7.addWidget(self.bgCopy_toolButton, 0, 2, 1, 1)

        self.bgDel_toolButton = QToolButton(self.layoutWidget2)
        self.bgDel_toolButton.setObjectName("bgDel_toolButton")
        self.bgDel_toolButton.setIcon(icon11)

        self.gridLayout_7.addWidget(self.bgDel_toolButton, 0, 3, 1, 1)

        self.bgPic_plainTextEdit = QPlainTextEdit(self.layoutWidget2)
        self.bgPic_plainTextEdit.setObjectName("bgPic_plainTextEdit")
        self.bgPic_plainTextEdit.setMinimumSize(QSize(285, 0))
        self.bgPic_plainTextEdit.setMaximumSize(QSize(16777215, 60))
        self.bgPic_plainTextEdit.setFont(font)
        self.bgPic_plainTextEdit.setReadOnly(True)

        self.gridLayout_7.addWidget(self.bgPic_plainTextEdit, 1, 0, 1, 4)

        self.bgPic_label = ClickableLabel(self.layoutWidget2)
        self.bgPic_label.setObjectName("bgPic_label")
        self.bgPic_label.setMinimumSize(QSize(259, 239))
        self.bgPic_label.setMaximumSize(QSize(16777215, 16777215))
        self.bgPic_label.setFont(font)
        self.bgPic_label.setFrameShape(QFrame.Box)

        self.gridLayout_7.addWidget(self.bgPic_label, 2, 0, 1, 4)

        self.gridLayout_9.addLayout(self.gridLayout_7, 0, 1, 1, 1)

        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_13 = QLabel(self.layoutWidget2)
        self.label_13.setObjectName("label_13")
        self.label_13.setMaximumSize(QSize(16777215, 28))
        self.label_13.setFont(font6)
        self.label_13.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_13.setAlignment(Qt.AlignCenter)

        self.gridLayout_8.addWidget(self.label_13, 0, 0, 1, 1)

        self.olOpen_toolButton = QToolButton(self.layoutWidget2)
        self.olOpen_toolButton.setObjectName("olOpen_toolButton")
        self.olOpen_toolButton.setIcon(icon12)

        self.gridLayout_8.addWidget(self.olOpen_toolButton, 0, 1, 1, 1)

        self.olDel_toolButton = QToolButton(self.layoutWidget2)
        self.olDel_toolButton.setObjectName("olDel_toolButton")
        self.olDel_toolButton.setIcon(icon11)

        self.gridLayout_8.addWidget(self.olDel_toolButton, 0, 2, 1, 1)

        self.olPic_plainTextEdit = QPlainTextEdit(self.layoutWidget2)
        self.olPic_plainTextEdit.setObjectName("olPic_plainTextEdit")
        self.olPic_plainTextEdit.setMinimumSize(QSize(286, 0))
        self.olPic_plainTextEdit.setMaximumSize(QSize(16777215, 60))
        self.olPic_plainTextEdit.setFont(font)
        self.olPic_plainTextEdit.setReadOnly(True)

        self.gridLayout_8.addWidget(self.olPic_plainTextEdit, 1, 0, 1, 3)

        self.olPic_label = ClickableLabel(self.layoutWidget2)
        self.olPic_label.setObjectName("olPic_label")
        self.olPic_label.setMinimumSize(QSize(259, 239))
        self.olPic_label.setMaximumSize(QSize(16777215, 16777215))
        self.olPic_label.setFont(font)
        self.olPic_label.setFrameShape(QFrame.Box)

        self.gridLayout_8.addWidget(self.olPic_label, 2, 0, 1, 3)

        self.gridLayout_9.addLayout(self.gridLayout_8, 0, 2, 1, 1)

        self.splitter.addWidget(self.layoutWidget2)
        self.splitter_2.addWidget(self.splitter)

        self.gridLayout_10.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.tabWidget.addTab(self.maintab, "")
        self.logtab = QWidget()
        self.logtab.setObjectName("logtab")
        self.gridLayout_11 = QGridLayout(self.logtab)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.log_plainTextEdit = QPlainTextEdit(self.logtab)
        self.log_plainTextEdit.setObjectName("log_plainTextEdit")
        self.log_plainTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.log_plainTextEdit.setReadOnly(True)
        self.log_plainTextEdit.setPlainText("")

        self.gridLayout_11.addWidget(self.log_plainTextEdit, 0, 0, 1, 1)

        self.tabWidget.addTab(self.logtab, "")

        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)

        ViewsWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(ViewsWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1400, 25))
        self.menuFile = QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuSettings = QMenu(self.menubar)
        self.menuSettings.setObjectName("menuSettings")
        self.menuHelp = QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        self.menuRun = QMenu(self.menubar)
        self.menuRun.setObjectName("menuRun")
        self.menuOther = QMenu(self.menubar)
        self.menuOther.setObjectName("menuOther")
        ViewsWindow.setMenuBar(self.menubar)
        self.toolBar = QToolBar(ViewsWindow)
        self.toolBar.setObjectName("toolBar")
        self.toolBar.setEnabled(True)
        self.toolBar.setFont(font)
        self.toolBar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        ViewsWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuSettings.menuAction())
        self.menubar.addAction(self.menuRun.menuAction())
        self.menubar.addAction(self.menuOther.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        self.menuFile.addAction(self.actionNew)
        self.menuFile.addAction(self.actionOpen)
        self.menuFile.addAction(self.actionClose)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionMedia)
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionQuit)
        self.menuSettings.addAction(self.actionTask_Configuration)
        self.menuSettings.addAction(self.actionTask_Actions)
        self.menuHelp.addAction(self.actionDocumentation)
        self.menuRun.addAction(self.actionRun_Environment)
        self.menuRun.addSeparator()
        self.menuRun.addAction(self.actionLocate_GEMSrun)
        self.menuOther.addAction(self.actionNetwork_Graph)
        self.menuOther.addSeparator()
        self.toolBar.addAction(self.actionNew)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionOpen)
        self.toolBar.addAction(self.actionSaveEnv)
        self.toolBar.addAction(self.actionClose)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionMedia)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionRun_Environment)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionTask_Configuration)
        self.toolBar.addAction(self.actionTask_Actions)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionNetwork_Graph)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionDocumentation)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionQuit)
        self.toolBar.addSeparator()

        self.retranslateUi(ViewsWindow)
        self.actionQuit.triggered.connect(ViewsWindow.close)

        self.tabWidget.setCurrentIndex(0)

        QMetaObject.connectSlotsByName(ViewsWindow)

    # setupUi

    def retranslateUi(self, ViewsWindow):
        ViewsWindow.setWindowTitle(QCoreApplication.translate("ViewsWindow", "GEMS Editor - 2021 v1.0", None))
        self.actionOpen.setText(QCoreApplication.translate("ViewsWindow", "Open", None))
        self.actionNew.setText(QCoreApplication.translate("ViewsWindow", "New", None))
        self.actionClose.setText(QCoreApplication.translate("ViewsWindow", "Close", None))
        self.actionQuit.setText(QCoreApplication.translate("ViewsWindow", "Quit", None))
        self.actionTask_Configuration.setText(QCoreApplication.translate("ViewsWindow", "Settings", None))
        # if QT_CONFIG(tooltip)
        self.actionTask_Configuration.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Edit Global Environmnet Settings", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionTask_Actions.setText(QCoreApplication.translate("ViewsWindow", "Actions", None))
        # if QT_CONFIG(tooltip)
        self.actionTask_Actions.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Edit Global Environment Actions", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionDocumentation.setText(QCoreApplication.translate("ViewsWindow", "Help", None))
        self.actionRun_Environment.setText(QCoreApplication.translate("ViewsWindow", "Run", None))
        # if QT_CONFIG(tooltip)
        self.actionRun_Environment.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Run Current GEMS Environment", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionMedia.setText(QCoreApplication.translate("ViewsWindow", "Media Folder", None))
        # if QT_CONFIG(tooltip)
        self.actionMedia.setToolTip(QCoreApplication.translate("ViewsWindow", "Launch Media Folder Viewer", None))
        # endif // QT_CONFIG(tooltip)
        self.actionLocate_GEMSrun.setText(QCoreApplication.translate("ViewsWindow", "Locate GEMSrun", None))
        self.actionSave.setText(QCoreApplication.translate("ViewsWindow", "Save", None))
        self.actionSaveEnv.setText(QCoreApplication.translate("ViewsWindow", "Save", None))
        # if QT_CONFIG(tooltip)
        self.actionSaveEnv.setToolTip(QCoreApplication.translate("ViewsWindow", "Save Changes To Environment", None))
        # endif // QT_CONFIG(tooltip)
        self.actionNetwork_Graph.setText(QCoreApplication.translate("ViewsWindow", "Network Graph", None))
        # if QT_CONFIG(tooltip)
        self.actionNetwork_Graph.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Launch Network Graph in Default Browser", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.label_4.setText(QCoreApplication.translate("ViewsWindow", "View List", None))
        self.label_6.setText("")
        # if QT_CONFIG(tooltip)
        self.viewDel_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Deleted the selected view", None))
        # endif // QT_CONFIG(tooltip)
        self.viewDel_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.viewAdd_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Add a new view", None))
        # endif // QT_CONFIG(tooltip)
        self.viewAdd_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        self.labelAppName.setText(QCoreApplication.translate("ViewsWindow", "GEMS Editor", None))
        self.label.setText(QCoreApplication.translate("ViewsWindow", "Current GEMS Environment: ", None))
        self.dbfilename_Label.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.objectsButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Manage objects for this view", None))
        # endif // QT_CONFIG(tooltip)
        self.objectsButton.setText(QCoreApplication.translate("ViewsWindow", "Objects", None))
        self.label_3.setText(QCoreApplication.translate("ViewsWindow", "View Action List", None))
        # if QT_CONFIG(tooltip)
        self.actionAdd_toolButton.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Add new blank action for this view", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionAdd_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.actionDel_toolButton.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Delete currently selected view action", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.actionDel_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        self.label_7.setText(QCoreApplication.translate("ViewsWindow", "Foreground Pic", None))
        # if QT_CONFIG(tooltip)
        self.fgOpen_toolButton.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Select foreground picture file", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.fgOpen_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.fgCopy_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Copy background picture", None))
        # endif // QT_CONFIG(tooltip)
        self.fgCopy_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.fgDel_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Clear foreground picture", None))
        # endif // QT_CONFIG(tooltip)
        self.fgDel_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        self.fgPic_label.setText("")
        self.label_8.setText(QCoreApplication.translate("ViewsWindow", "Background Pic", None))
        # if QT_CONFIG(tooltip)
        self.bgOpen_toolButton.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Select background picture file", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.bgOpen_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.bgCopy_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Copy foreground picture", None))
        # endif // QT_CONFIG(tooltip)
        self.bgCopy_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.bgDel_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Clear background picture", None))
        # endif // QT_CONFIG(tooltip)
        self.bgDel_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        self.bgPic_label.setText("")
        self.label_13.setText(QCoreApplication.translate("ViewsWindow", "Overlay Pic", None))
        # if QT_CONFIG(tooltip)
        self.olOpen_toolButton.setToolTip(
            QCoreApplication.translate("ViewsWindow", "Select overlay picture file", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.olOpen_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        # if QT_CONFIG(tooltip)
        self.olDel_toolButton.setToolTip(QCoreApplication.translate("ViewsWindow", "Clear overlay picture", None))
        # endif // QT_CONFIG(tooltip)
        self.olDel_toolButton.setText(QCoreApplication.translate("ViewsWindow", "...", None))
        self.olPic_plainTextEdit.setPlainText("")
        self.olPic_label.setText("")
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.maintab), QCoreApplication.translate("ViewsWindow", "Main", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.logtab), QCoreApplication.translate("ViewsWindow", "Log", None)
        )
        self.menuFile.setTitle(QCoreApplication.translate("ViewsWindow", "File", None))
        self.menuSettings.setTitle(QCoreApplication.translate("ViewsWindow", "Settings", None))
        self.menuHelp.setTitle(QCoreApplication.translate("ViewsWindow", "Help", None))
        self.menuRun.setTitle(QCoreApplication.translate("ViewsWindow", "Run", None))
        self.menuOther.setTitle(QCoreApplication.translate("ViewsWindow", "Other", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("ViewsWindow", "toolBar", None))

    # retranslateUi
