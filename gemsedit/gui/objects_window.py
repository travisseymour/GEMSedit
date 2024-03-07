# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'objects_window.ui'
##
## Created by: Qt User Interface Compiler version 6.6.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QCheckBox,
    QDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSplitter,
    QTableView,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from gemsedit.gui.CustomClickableLabel import ClickableLabel
from gemsedit.gui import gemsedit_rc


class Ui_ObjectsWindow(object):
    def setupUi(self, ObjectsWindow):
        if not ObjectsWindow.objectName():
            ObjectsWindow.setObjectName("ObjectsWindow")
        ObjectsWindow.setWindowModality(Qt.NonModal)
        ObjectsWindow.resize(1203, 732)
        ObjectsWindow.setMinimumSize(QSize(1145, 720))
        ObjectsWindow.setMaximumSize(QSize(5000, 5000))
        ObjectsWindow.setBaseSize(QSize(1200, 720))
        font = QFont()
        font.setFamilies(["Verdana"])
        ObjectsWindow.setFont(font)
        ObjectsWindow.setModal(False)
        self.gridLayout_3 = QGridLayout(ObjectsWindow)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.splitter_2 = QSplitter(ObjectsWindow)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter_2.setOrientation(Qt.Horizontal)
        self.layoutWidget = QWidget(self.splitter_2)
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout_2 = QGridLayout(self.layoutWidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.labelAppName = QLabel(self.layoutWidget)
        self.labelAppName.setObjectName("labelAppName")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelAppName.sizePolicy().hasHeightForWidth())
        self.labelAppName.setSizePolicy(sizePolicy)
        font1 = QFont()
        font1.setFamilies(["Verdana"])
        font1.setPointSize(24)
        font1.setBold(True)
        self.labelAppName.setFont(font1)

        self.gridLayout_2.addWidget(self.labelAppName, 0, 0, 1, 2)

        self.horizontalSpacer = QSpacerItem(
            18, 20, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_2.addItem(self.horizontalSpacer, 0, 2, 1, 1)

        self.label_6 = QLabel(self.layoutWidget)
        self.label_6.setObjectName("label_6")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy1)
        self.label_6.setMaximumSize(QSize(50, 50))
        self.label_6.setPixmap(
            QPixmap(":/newPrefix/media/Antialiasfactory-Jewelry-Agate.ico")
        )
        self.label_6.setScaledContents(True)

        self.gridLayout_2.addWidget(self.label_6, 0, 3, 1, 2)

        self.label_4 = QLabel(self.layoutWidget)
        self.label_4.setObjectName("label_4")
        font2 = QFont()
        font2.setFamilies(["Verdana"])
        font2.setPointSize(22)
        font2.setItalic(False)
        self.label_4.setFont(font2)
        self.label_4.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_4.setAlignment(Qt.AlignCenter)

        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)

        self.horizontalSpacer_6 = QSpacerItem(
            80, 28, QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Minimum
        )

        self.gridLayout_2.addItem(self.horizontalSpacer_6, 1, 1, 1, 2)

        self.objectAdd_toolButton = QToolButton(self.layoutWidget)
        self.objectAdd_toolButton.setObjectName("objectAdd_toolButton")
        icon = QIcon()
        icon.addFile(":/newPrefix/media/add-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.objectAdd_toolButton.setIcon(icon)

        self.gridLayout_2.addWidget(self.objectAdd_toolButton, 1, 3, 1, 1)

        self.objectDel_toolButton = QToolButton(self.layoutWidget)
        self.objectDel_toolButton.setObjectName("objectDel_toolButton")
        icon1 = QIcon()
        icon1.addFile(
            ":/newPrefix/media/delete-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.objectDel_toolButton.setIcon(icon1)

        self.gridLayout_2.addWidget(self.objectDel_toolButton, 1, 4, 1, 1)

        self.object_tableView = QTableView(self.layoutWidget)
        self.object_tableView.setObjectName("object_tableView")
        sizePolicy2 = QSizePolicy(
            QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(
            self.object_tableView.sizePolicy().hasHeightForWidth()
        )
        self.object_tableView.setSizePolicy(sizePolicy2)
        self.object_tableView.setMaximumSize(QSize(16777215, 16777215))
        font3 = QFont()
        font3.setFamilies(["Verdana"])
        font3.setPointSize(14)
        font3.setBold(True)
        self.object_tableView.setFont(font3)
        self.object_tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.object_tableView.setDragEnabled(True)
        self.object_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.object_tableView.setAlternatingRowColors(True)
        self.object_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.object_tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.object_tableView.horizontalHeader().setVisible(False)
        self.object_tableView.horizontalHeader().setStretchLastSection(True)
        self.object_tableView.verticalHeader().setVisible(False)

        self.gridLayout_2.addWidget(self.object_tableView, 2, 0, 1, 5)

        self.splitter_2.addWidget(self.layoutWidget)
        self.splitter = QSplitter(self.splitter_2)
        self.splitter.setObjectName("splitter")
        self.splitter.setOrientation(Qt.Vertical)
        self.layoutWidget1 = QWidget(self.splitter)
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.visible_checkBox = QCheckBox(self.layoutWidget1)
        self.visible_checkBox.setObjectName("visible_checkBox")
        self.visible_checkBox.setMinimumSize(QSize(200, 0))
        self.visible_checkBox.setFont(font3)
        self.visible_checkBox.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_7.addWidget(self.visible_checkBox)

        self.takeable_checkBox = QCheckBox(self.layoutWidget1)
        self.takeable_checkBox.setObjectName("takeable_checkBox")
        self.takeable_checkBox.setMinimumSize(QSize(200, 0))
        self.takeable_checkBox.setFont(font3)
        self.takeable_checkBox.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_7.addWidget(self.takeable_checkBox)

        self.draggable_checkBox = QCheckBox(self.layoutWidget1)
        self.draggable_checkBox.setObjectName("draggable_checkBox")
        self.draggable_checkBox.setMinimumSize(QSize(200, 0))
        self.draggable_checkBox.setFont(font3)
        self.draggable_checkBox.setLayoutDirection(Qt.RightToLeft)

        self.horizontalLayout_7.addWidget(self.draggable_checkBox)

        self.horizontalSpacer_7 = QSpacerItem(
            158, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_7.addItem(self.horizontalSpacer_7)

        self.gridLayout.addLayout(self.horizontalLayout_7, 1, 0, 2, 1)

        self.closeButton = QPushButton(self.layoutWidget1)
        self.closeButton.setObjectName("closeButton")
        font4 = QFont()
        font4.setFamilies(["Verdana"])
        font4.setPointSize(16)
        font4.setItalic(False)
        self.closeButton.setFont(font4)

        self.gridLayout.addWidget(self.closeButton, 0, 1, 2, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_9 = QLabel(self.layoutWidget1)
        self.label_9.setObjectName("label_9")
        self.label_9.setFont(font3)
        self.label_9.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.label_9)

        self.parent_Label = QLabel(self.layoutWidget1)
        self.parent_Label.setObjectName("parent_Label")
        self.parent_Label.setMinimumSize(QSize(290, 0))
        font5 = QFont()
        font5.setFamilies(["Helvetica"])
        font5.setPointSize(18)
        font5.setBold(False)
        self.parent_Label.setFont(font5)
        self.parent_Label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)

        self.horizontalLayout_5.addWidget(self.parent_Label)

        self.horizontalSpacer_2 = QSpacerItem(
            158, 18, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_5.addItem(self.horizontalSpacer_2)

        self.gridLayout.addLayout(self.horizontalLayout_5, 0, 0, 1, 1)

        self.verticalLayout_4.addLayout(self.gridLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_3 = QLabel(self.layoutWidget1)
        self.label_3.setObjectName("label_3")
        self.label_3.setFont(font4)
        self.label_3.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_3.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_2.addWidget(self.label_3)

        self.horizontalSpacer_4 = QSpacerItem(
            538, 28, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.actionAdd_toolButton = QToolButton(self.layoutWidget1)
        self.actionAdd_toolButton.setObjectName("actionAdd_toolButton")
        self.actionAdd_toolButton.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.actionAdd_toolButton)

        self.actionDel_toolButton = QToolButton(self.layoutWidget1)
        self.actionDel_toolButton.setObjectName("actionDel_toolButton")
        self.actionDel_toolButton.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.actionDel_toolButton)

        self.verticalLayout_4.addLayout(self.horizontalLayout_2)

        self.OAL_tableView = QTableView(self.layoutWidget1)
        self.OAL_tableView.setObjectName("OAL_tableView")
        self.OAL_tableView.setMinimumSize(QSize(0, 200))
        self.OAL_tableView.setMaximumSize(QSize(16777215, 16777215))
        font6 = QFont()
        font6.setFamilies(["Verdana"])
        font6.setPointSize(12)
        self.OAL_tableView.setFont(font6)
        self.OAL_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.OAL_tableView.setDragEnabled(True)
        self.OAL_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.OAL_tableView.setAlternatingRowColors(True)
        self.OAL_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.OAL_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.OAL_tableView.horizontalHeader().setStretchLastSection(True)
        self.OAL_tableView.verticalHeader().setVisible(False)

        self.verticalLayout_4.addWidget(self.OAL_tableView)

        self.splitter.addWidget(self.layoutWidget1)
        self.layoutWidget2 = QWidget(self.splitter)
        self.layoutWidget2.setObjectName("layoutWidget2")
        self.horizontalLayout_6 = QHBoxLayout(self.layoutWidget2)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_7 = QLabel(self.layoutWidget2)
        self.label_7.setObjectName("label_7")
        self.label_7.setMinimumSize(QSize(0, 28))
        self.label_7.setMaximumSize(QSize(16777215, 28))
        font7 = QFont()
        font7.setFamilies(["Verdana"])
        font7.setPointSize(14)
        font7.setBold(False)
        font7.setItalic(False)
        self.label_7.setFont(font7)
        self.label_7.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_7.setAlignment(Qt.AlignCenter)

        self.horizontalLayout.addWidget(self.label_7)

        self.drawSelect_toolButton = QToolButton(self.layoutWidget2)
        self.drawSelect_toolButton.setObjectName("drawSelect_toolButton")
        self.drawSelect_toolButton.setEnabled(True)
        icon2 = QIcon()
        icon2.addFile(
            ":/newPrefix/media/selection_arrow-256.png",
            QSize(),
            QIcon.Normal,
            QIcon.Off,
        )
        self.drawSelect_toolButton.setIcon(icon2)

        self.horizontalLayout.addWidget(self.drawSelect_toolButton)

        self.delSelect_toolButton = QToolButton(self.layoutWidget2)
        self.delSelect_toolButton.setObjectName("delSelect_toolButton")
        self.delSelect_toolButton.setIcon(icon1)

        self.horizontalLayout.addWidget(self.delSelect_toolButton)

        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.objectPic_label = QLabel(self.layoutWidget2)
        self.objectPic_label.setObjectName("objectPic_label")
        self.objectPic_label.setMinimumSize(QSize(350, 300))
        self.objectPic_label.setMaximumSize(QSize(350, 300))
        self.objectPic_label.setFont(font6)
        self.objectPic_label.setFrameShape(QFrame.Box)

        self.verticalLayout_2.addWidget(self.objectPic_label)

        self.horizontalLayout_6.addLayout(self.verticalLayout_2)

        self.horizontalSpacer_3 = QSpacerItem(
            58, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.label_8 = QLabel(self.layoutWidget2)
        self.label_8.setObjectName("label_8")
        self.label_8.setMinimumSize(QSize(0, 28))
        self.label_8.setMaximumSize(QSize(16777215, 28))
        self.label_8.setFont(font7)
        self.label_8.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.label_8.setAlignment(Qt.AlignCenter)

        self.horizontalLayout_4.addWidget(self.label_8)

        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.objectLocPic_label = ClickableLabel(self.layoutWidget2)
        self.objectLocPic_label.setObjectName("objectLocPic_label")
        self.objectLocPic_label.setMinimumSize(QSize(350, 300))
        self.objectLocPic_label.setMaximumSize(QSize(350, 300))
        self.objectLocPic_label.setFont(font6)
        self.objectLocPic_label.setFrameShape(QFrame.Box)

        self.verticalLayout_3.addWidget(self.objectLocPic_label)

        self.horizontalLayout_6.addLayout(self.verticalLayout_3)

        self.splitter.addWidget(self.layoutWidget2)
        self.splitter_2.addWidget(self.splitter)

        self.gridLayout_3.addWidget(self.splitter_2, 0, 0, 1, 1)

        self.retranslateUi(ObjectsWindow)
        self.closeButton.pressed.connect(ObjectsWindow.close)

        QMetaObject.connectSlotsByName(ObjectsWindow)

    # setupUi

    def retranslateUi(self, ObjectsWindow):
        ObjectsWindow.setWindowTitle(
            QCoreApplication.translate("ObjectsWindow", "GEMS Object Editor", None)
        )
        self.labelAppName.setText(
            QCoreApplication.translate("ObjectsWindow", "GEMS Editor", None)
        )
        self.label_6.setText("")
        self.label_4.setText(
            QCoreApplication.translate("ObjectsWindow", "Object List", None)
        )
        self.objectAdd_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.objectDel_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.visible_checkBox.setText(
            QCoreApplication.translate("ObjectsWindow", "Visible? ", None)
        )
        self.takeable_checkBox.setText(
            QCoreApplication.translate("ObjectsWindow", "Takeable? ", None)
        )
        self.draggable_checkBox.setText(
            QCoreApplication.translate("ObjectsWindow", "Draggable?", None)
        )
        self.closeButton.setText(
            QCoreApplication.translate("ObjectsWindow", "Close", None)
        )
        self.label_9.setText(
            QCoreApplication.translate("ObjectsWindow", "Parent View:", None)
        )
        self.parent_Label.setText(
            QCoreApplication.translate("ObjectsWindow", "-", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("ObjectsWindow", "Object Action List", None)
        )
        self.actionAdd_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.actionDel_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.label_7.setText(
            QCoreApplication.translate("ObjectsWindow", "Object Pic", None)
        )
        self.drawSelect_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.delSelect_toolButton.setText(
            QCoreApplication.translate("ObjectsWindow", "...", None)
        )
        self.objectPic_label.setText("")
        self.label_8.setText(
            QCoreApplication.translate("ObjectsWindow", "Object Location in View", None)
        )
        self.objectLocPic_label.setText("")

    # retranslateUi
