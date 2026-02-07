# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'settings_dlg.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDialog, QFrame,
    QGridLayout, QHBoxLayout, QHeaderView, QLabel,
    QPushButton, QSizePolicy, QSpacerItem, QTableView,
    QWidget)
import gemsedit.gui.gemsedit_rc

class Ui_SettingsDialog(object):
    def setupUi(self, SettingsDialog):
        if not SettingsDialog.objectName():
            SettingsDialog.setObjectName(u"SettingsDialog")
        SettingsDialog.setWindowModality(Qt.NonModal)
        SettingsDialog.resize(800, 601)
        SettingsDialog.setMinimumSize(QSize(640, 480))
        font = QFont()
        font.setFamilies([u"Arial"])
        SettingsDialog.setFont(font)
        SettingsDialog.setModal(False)
        self.gridLayout_2 = QGridLayout(SettingsDialog)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName(u"gridLayout")
        self.Label9 = QLabel(SettingsDialog)
        self.Label9.setObjectName(u"Label9")
        font1 = QFont()
        font1.setFamilies([u"Arial"])
        font1.setPointSize(14)
        font1.setItalic(False)
        self.Label9.setFont(font1)
        self.Label9.setAlignment(Qt.AlignBottom|Qt.AlignLeading|Qt.AlignLeft)

        self.gridLayout.addWidget(self.Label9, 4, 0, 1, 2)

        self.xxHelpLabel = QLabel(SettingsDialog)
        self.xxHelpLabel.setObjectName(u"xxHelpLabel")
        self.xxHelpLabel.setMinimumSize(QSize(0, 60))
        font2 = QFont()
        font2.setFamilies([u"Arial"])
        font2.setPointSize(14)
        font2.setBold(False)
        font2.setItalic(False)
        self.xxHelpLabel.setFont(font2)
        self.xxHelpLabel.setStyleSheet(u"background: rgb(255, 255, 255)")
        self.xxHelpLabel.setFrameShape(QFrame.Box)
        self.xxHelpLabel.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)
        self.xxHelpLabel.setWordWrap(True)

        self.gridLayout.addWidget(self.xxHelpLabel, 5, 0, 1, 2)

        self.settings_tableView = QTableView(SettingsDialog)
        self.settings_tableView.setObjectName(u"settings_tableView")
        font3 = QFont()
        font3.setFamilies([u"Arial"])
        font3.setPointSize(14)
        self.settings_tableView.setFont(font3)
        self.settings_tableView.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.settings_tableView.setAlternatingRowColors(True)
        self.settings_tableView.setSelectionMode(QAbstractItemView.SingleSelection)
        self.settings_tableView.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.settings_tableView.horizontalHeader().setVisible(False)
        self.settings_tableView.horizontalHeader().setStretchLastSection(True)
        self.settings_tableView.verticalHeader().setVisible(True)
        self.settings_tableView.verticalHeader().setStretchLastSection(False)

        self.gridLayout.addWidget(self.settings_tableView, 2, 1, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.label_5 = QLabel(SettingsDialog)
        self.label_5.setObjectName(u"label_5")
        font4 = QFont()
        font4.setFamilies([u"Arial"])
        font4.setPointSize(24)
        font4.setBold(True)
        self.label_5.setFont(font4)

        self.horizontalLayout_3.addWidget(self.label_5)

        self.horizontalSpacer = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_6 = QLabel(SettingsDialog)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setMaximumSize(QSize(50, 50))
        self.label_6.setPixmap(QPixmap(u":/newPrefix/media/Agate-icon.png"))
        self.label_6.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label_6)


        self.horizontalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(148, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.applyButton = QPushButton(SettingsDialog)
        self.applyButton.setObjectName(u"applyButton")
        font5 = QFont()
        font5.setFamilies([u"Arial"])
        font5.setPointSize(16)
        font5.setItalic(False)
        self.applyButton.setFont(font5)

        self.horizontalLayout.addWidget(self.applyButton)


        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 2)

        self.label_2 = QLabel(SettingsDialog)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setFont(font5)

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 2)


        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)


        self.retranslateUi(SettingsDialog)

        QMetaObject.connectSlotsByName(SettingsDialog)
    # setupUi

    def retranslateUi(self, SettingsDialog):
        SettingsDialog.setWindowTitle(QCoreApplication.translate("SettingsDialog", u"Dialog", None))
        self.Label9.setText(QCoreApplication.translate("SettingsDialog", u"Description:", None))
        self.xxHelpLabel.setText(QCoreApplication.translate("SettingsDialog", u"...", None))
        self.label_5.setText(QCoreApplication.translate("SettingsDialog", u"GEMS Editor", None))
        self.label_6.setText("")
        self.applyButton.setText(QCoreApplication.translate("SettingsDialog", u"Close", None))
        self.label_2.setText(QCoreApplication.translate("SettingsDialog", u"Environment Settings List", None))
    # retranslateUi

