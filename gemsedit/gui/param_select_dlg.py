# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'param_select_dlg.ui'
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
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QTableView,
    QWidget,
)
from gemsedit.gui import gemsedit_rc


class Ui_parameterSelectDialog(object):
    def setupUi(self, parameterSelectDialog):
        if not parameterSelectDialog.objectName():
            parameterSelectDialog.setObjectName("parameterSelectDialog")
        parameterSelectDialog.setWindowModality(Qt.NonModal)
        parameterSelectDialog.resize(631, 589)
        font = QFont()
        font.setFamilies(["Verdana"])
        parameterSelectDialog.setFont(font)
        self.gridLayout_2 = QGridLayout(parameterSelectDialog)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.xx_tableView = QTableView(parameterSelectDialog)
        self.xx_tableView.setObjectName("xx_tableView")
        font1 = QFont()
        font1.setFamilies(["Verdana"])
        font1.setPointSize(12)
        self.xx_tableView.setFont(font1)
        self.xx_tableView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.xx_tableView.setAlternatingRowColors(True)
        self.xx_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.xx_tableView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.xx_tableView.horizontalHeader().setVisible(False)
        self.xx_tableView.horizontalHeader().setStretchLastSection(True)
        self.xx_tableView.verticalHeader().setVisible(False)

        self.gridLayout.addWidget(self.xx_tableView, 3, 0, 1, 1)

        self.xxparamLabel = QLabel(parameterSelectDialog)
        self.xxparamLabel.setObjectName("xxparamLabel")
        font2 = QFont()
        font2.setFamilies(["Verdana"])
        font2.setPointSize(16)
        font2.setItalic(False)
        self.xxparamLabel.setFont(font2)
        self.xxparamLabel.setStyleSheet("background-color: rgb(255, 204, 102);")
        self.xxparamLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.xxparamLabel, 2, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelAppName = QLabel(parameterSelectDialog)
        self.labelAppName.setObjectName("labelAppName")
        font3 = QFont()
        font3.setFamilies(["Verdana"])
        font3.setPointSize(24)
        font3.setBold(True)
        self.labelAppName.setFont(font3)

        self.horizontalLayout_3.addWidget(self.labelAppName)

        self.horizontalSpacer = QSpacerItem(
            18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_6 = QLabel(parameterSelectDialog)
        self.label_6.setObjectName("label_6")
        self.label_6.setMaximumSize(QSize(50, 50))
        self.label_6.setPixmap(
            QPixmap(":/newPrefix/media/Antialiasfactory-Jewelry-Agate.ico")
        )
        self.label_6.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label_6)

        self.horizontalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(
            148, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum
        )

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.cancelButton = QPushButton(parameterSelectDialog)
        self.cancelButton.setObjectName("cancelButton")
        font4 = QFont()
        font4.setFamilies(["Verdana"])
        font4.setPointSize(16)
        self.cancelButton.setFont(font4)

        self.horizontalLayout.addWidget(self.cancelButton)

        self.applyButton = QPushButton(parameterSelectDialog)
        self.applyButton.setObjectName("applyButton")
        self.applyButton.setFont(font2)
        self.applyButton.setAutoDefault(False)

        self.horizontalLayout.addWidget(self.applyButton)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)

        self.xxparam_tableView = QTableView(parameterSelectDialog)
        self.xxparam_tableView.setObjectName("xxparam_tableView")
        self.xxparam_tableView.setFont(font1)
        self.xxparam_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.xxparam_tableView.setAlternatingRowColors(True)
        self.xxparam_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.xxparam_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.xxparam_tableView.horizontalHeader().setVisible(False)
        self.xxparam_tableView.horizontalHeader().setStretchLastSection(True)
        self.xxparam_tableView.verticalHeader().setVisible(True)
        self.xxparam_tableView.verticalHeader().setStretchLastSection(False)

        self.gridLayout.addWidget(self.xxparam_tableView, 3, 1, 1, 1)

        self.resultLabel = QLabel(parameterSelectDialog)
        self.resultLabel.setObjectName("resultLabel")
        self.resultLabel.setMinimumSize(QSize(0, 60))
        font5 = QFont()
        font5.setFamilies(["Verdana"])
        font5.setPointSize(12)
        font5.setBold(False)
        font5.setItalic(False)
        self.resultLabel.setFont(font5)
        self.resultLabel.setStyleSheet("background: rgb(255, 255, 255)")
        self.resultLabel.setFrameShape(QFrame.Box)
        self.resultLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.resultLabel.setWordWrap(True)

        self.gridLayout.addWidget(self.resultLabel, 8, 0, 1, 2)

        self.titleLabel = QLabel(parameterSelectDialog)
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setFont(font2)
        self.titleLabel.setStyleSheet("background-color: rgb(102, 204, 255)")
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.titleLabel, 1, 0, 1, 2)

        self.xxHelpLabel = QLabel(parameterSelectDialog)
        self.xxHelpLabel.setObjectName("xxHelpLabel")
        self.xxHelpLabel.setMinimumSize(QSize(0, 60))
        self.xxHelpLabel.setFont(font5)
        self.xxHelpLabel.setStyleSheet("background: rgb(255, 255, 255)")
        self.xxHelpLabel.setFrameShape(QFrame.Box)
        self.xxHelpLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignVCenter)
        self.xxHelpLabel.setWordWrap(True)

        self.gridLayout.addWidget(self.xxHelpLabel, 6, 0, 1, 2)

        self.Label9 = QLabel(parameterSelectDialog)
        self.Label9.setObjectName("Label9")
        font6 = QFont()
        font6.setFamilies(["Verdana"])
        font6.setPointSize(14)
        font6.setItalic(False)
        self.Label9.setFont(font6)
        self.Label9.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.gridLayout.addWidget(self.Label9, 5, 0, 1, 2)

        self.xxLabel = QLabel(parameterSelectDialog)
        self.xxLabel.setObjectName("xxLabel")
        self.xxLabel.setFont(font2)
        self.xxLabel.setStyleSheet("background-color: rgb(255, 204, 102);")
        self.xxLabel.setAlignment(Qt.AlignCenter)

        self.gridLayout.addWidget(self.xxLabel, 2, 0, 1, 1)

        self.Label9_2 = QLabel(parameterSelectDialog)
        self.Label9_2.setObjectName("Label9_2")
        self.Label9_2.setFont(font6)
        self.Label9_2.setAlignment(Qt.AlignBottom | Qt.AlignLeading | Qt.AlignLeft)

        self.gridLayout.addWidget(self.Label9_2, 7, 0, 1, 2)

        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)

        self.retranslateUi(parameterSelectDialog)

        QMetaObject.connectSlotsByName(parameterSelectDialog)

    # setupUi

    def retranslateUi(self, parameterSelectDialog):
        parameterSelectDialog.setWindowTitle(
            QCoreApplication.translate("parameterSelectDialog", "Dialog", None)
        )
        self.xxparamLabel.setText(
            QCoreApplication.translate(
                "parameterSelectDialog", "XX Parameter List", None
            )
        )
        self.labelAppName.setText(
            QCoreApplication.translate("parameterSelectDialog", "GEMS Editor", None)
        )
        self.label_6.setText("")
        self.cancelButton.setText(
            QCoreApplication.translate("parameterSelectDialog", "Cancel", None)
        )
        self.applyButton.setText(
            QCoreApplication.translate("parameterSelectDialog", "Apply", None)
        )
        self.resultLabel.setText(
            QCoreApplication.translate("parameterSelectDialog", "...", None)
        )
        self.titleLabel.setText(
            QCoreApplication.translate(
                "parameterSelectDialog", "Action XX Editor", None
            )
        )
        self.xxHelpLabel.setText(
            QCoreApplication.translate("parameterSelectDialog", "...", None)
        )
        self.Label9.setText(
            QCoreApplication.translate("parameterSelectDialog", "Description:", None)
        )
        self.xxLabel.setText(
            QCoreApplication.translate("parameterSelectDialog", "XX List", None)
        )
        self.Label9_2.setText(
            QCoreApplication.translate("parameterSelectDialog", "Result:", None)
        )

    # retranslateUi
