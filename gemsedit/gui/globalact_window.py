# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'globalact_window.ui'
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
    QDialog,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QToolButton,
    QWidget,
)
from gemsedit.gui import gemsedit_rc


class Ui_GlobalActionsDialog(object):
    def setupUi(self, GlobalActionsDialog):
        if not GlobalActionsDialog.objectName():
            GlobalActionsDialog.setObjectName("GlobalActionsDialog")
        GlobalActionsDialog.setWindowModality(Qt.NonModal)
        GlobalActionsDialog.resize(805, 692)
        font = QFont()
        font.setFamilies(["Verdana"])
        GlobalActionsDialog.setFont(font)
        self.gridLayout_2 = QGridLayout(GlobalActionsDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelAppName = QLabel(GlobalActionsDialog)
        self.labelAppName.setObjectName("labelAppName")
        font1 = QFont()
        font1.setFamilies(["Verdana"])
        font1.setPointSize(24)
        font1.setBold(True)
        self.labelAppName.setFont(font1)

        self.horizontalLayout_3.addWidget(self.labelAppName)

        self.label_8 = QLabel(GlobalActionsDialog)
        self.label_8.setObjectName("label_8")
        self.label_8.setMaximumSize(QSize(50, 50))
        self.label_8.setPixmap(
            QPixmap(":/newPrefix/media/Antialiasfactory-Jewelry-Agate.ico")
        )
        self.label_8.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label_8)

        self.horizontalSpacer_4 = QSpacerItem(
            18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer_4)

        self.gridLayout.addLayout(self.horizontalLayout_3, 0, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QLabel(GlobalActionsDialog)
        self.label.setObjectName("label")
        font2 = QFont()
        font2.setFamilies(["Verdana"])
        font2.setPointSize(22)
        font2.setItalic(False)
        self.label.setFont(font2)

        self.horizontalLayout.addWidget(self.label)

        self.horizontalSpacer = QSpacerItem(
            40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.closeButton = QPushButton(GlobalActionsDialog)
        self.closeButton.setObjectName("closeButton")
        font3 = QFont()
        font3.setFamilies(["Verdana"])
        font3.setPointSize(16)
        font3.setItalic(False)
        self.closeButton.setFont(font3)

        self.horizontalLayout.addWidget(self.closeButton)

        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.label_2 = QLabel(GlobalActionsDialog)
        self.label_2.setObjectName("label_2")
        font4 = QFont()
        font4.setFamilies(["Verdana"])
        font4.setPointSize(14)
        font4.setItalic(False)
        self.label_2.setFont(font4)

        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)

        self.GAL_tableView = QTableView(GlobalActionsDialog)
        self.GAL_tableView.setObjectName("GAL_tableView")
        font5 = QFont()
        font5.setFamilies(["Verdana"])
        font5.setPointSize(12)
        self.GAL_tableView.setFont(font5)
        self.GAL_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.GAL_tableView.setDragEnabled(True)
        self.GAL_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.GAL_tableView.setAlternatingRowColors(True)
        self.GAL_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.GAL_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.GAL_tableView.horizontalHeader().setStretchLastSection(True)
        self.GAL_tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.GAL_tableView, 3, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalSpacer_2 = QSpacerItem(
            638, 38, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_4.addItem(self.horizontalSpacer_2)

        self.gaAdd_toolButton = QToolButton(GlobalActionsDialog)
        self.gaAdd_toolButton.setObjectName("gaAdd_toolButton")
        icon = QIcon()
        icon.addFile(":/newPrefix/media/add-icon.png", QSize(), QIcon.Normal, QIcon.Off)
        self.gaAdd_toolButton.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.gaAdd_toolButton)

        self.gaDel_toolButton = QToolButton(GlobalActionsDialog)
        self.gaDel_toolButton.setObjectName("gaDel_toolButton")
        icon1 = QIcon()
        icon1.addFile(
            ":/newPrefix/media/delete-icon.png", QSize(), QIcon.Normal, QIcon.Off
        )
        self.gaDel_toolButton.setIcon(icon1)

        self.horizontalLayout_4.addWidget(self.gaDel_toolButton)

        self.gridLayout.addLayout(self.horizontalLayout_4, 4, 0, 1, 1)

        self.label_3 = QLabel(GlobalActionsDialog)
        self.label_3.setObjectName("label_3")
        self.label_3.setFont(font4)

        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)

        self.PAL_tableView = QTableView(GlobalActionsDialog)
        self.PAL_tableView.setObjectName("PAL_tableView")
        self.PAL_tableView.setFont(font5)
        self.PAL_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.PAL_tableView.setDragEnabled(True)
        self.PAL_tableView.setDragDropMode(QAbstractItemView.InternalMove)
        self.PAL_tableView.setAlternatingRowColors(True)
        self.PAL_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.PAL_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.PAL_tableView.horizontalHeader().setStretchLastSection(True)
        self.PAL_tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.PAL_tableView, 6, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.horizontalSpacer_3 = QSpacerItem(
            638, 38, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_5.addItem(self.horizontalSpacer_3)

        self.paAdd_toolButton = QToolButton(GlobalActionsDialog)
        self.paAdd_toolButton.setObjectName("paAdd_toolButton")
        self.paAdd_toolButton.setIcon(icon)

        self.horizontalLayout_5.addWidget(self.paAdd_toolButton)

        self.paDel_toolButton = QToolButton(GlobalActionsDialog)
        self.paDel_toolButton.setObjectName("paDel_toolButton")
        self.paDel_toolButton.setIcon(icon1)

        self.horizontalLayout_5.addWidget(self.paDel_toolButton)

        self.gridLayout.addLayout(self.horizontalLayout_5, 7, 0, 1, 1)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(GlobalActionsDialog)
        self.closeButton.pressed.connect(GlobalActionsDialog.close)

        QMetaObject.connectSlotsByName(GlobalActionsDialog)

    # setupUi

    def retranslateUi(self, GlobalActionsDialog):
        GlobalActionsDialog.setWindowTitle(
            QCoreApplication.translate(
                "GlobalActionsDialog", "Task Action Editor", None
            )
        )
        self.labelAppName.setText(
            QCoreApplication.translate("GlobalActionsDialog", "GEMS Editor", None)
        )
        self.label_8.setText("")
        self.label.setText(
            QCoreApplication.translate(
                "GlobalActionsDialog", "Global Environment Actions", None
            )
        )
        self.closeButton.setText(
            QCoreApplication.translate("GlobalActionsDialog", "Close", None)
        )
        self.label_2.setText(
            QCoreApplication.translate(
                "GlobalActionsDialog", "Global Action List", None
            )
        )
        self.gaAdd_toolButton.setText(
            QCoreApplication.translate("GlobalActionsDialog", "...", None)
        )
        self.gaDel_toolButton.setText(
            QCoreApplication.translate("GlobalActionsDialog", "...", None)
        )
        self.label_3.setText(
            QCoreApplication.translate(
                "GlobalActionsDialog", "Pocket Action List", None
            )
        )
        self.paAdd_toolButton.setText(
            QCoreApplication.translate("GlobalActionsDialog", "...", None)
        )
        self.paDel_toolButton.setText(
            QCoreApplication.translate("GlobalActionsDialog", "...", None)
        )

    # retranslateUi
