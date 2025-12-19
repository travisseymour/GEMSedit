
################################################################################
## Form generated from reading UI file 'run_launch_dlg.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import QCoreApplication, QMetaObject, QSize, Qt
from PySide6.QtGui import QFont, QIcon, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QPushButton,
    QRadioButton,
    QSizePolicy,
    QSpacerItem,
    QToolButton,
    QVBoxLayout,
)

import gemsedit.gui.gemsedit_rc  # noqa: F401


class Ui_GEMSRunDialog:
    def setupUi(self, GEMSRunDialog):
        if not GEMSRunDialog.objectName():
            GEMSRunDialog.setObjectName("GEMSRunDialog")
        GEMSRunDialog.setWindowModality(Qt.ApplicationModal)
        GEMSRunDialog.resize(803, 602)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(GEMSRunDialog.sizePolicy().hasHeightForWidth())
        GEMSRunDialog.setSizePolicy(sizePolicy)
        GEMSRunDialog.setMinimumSize(QSize(600, 480))
        GEMSRunDialog.setMaximumSize(QSize(5000, 5000))
        font = QFont()
        font.setFamilies(["Verdana"])
        font.setPointSize(12)
        font.setUnderline(True)
        GEMSRunDialog.setFont(font)
        GEMSRunDialog.setModal(True)
        self.horizontalLayout_10 = QHBoxLayout(GEMSRunDialog)
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.horizontalSpacer_5 = QSpacerItem(58, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_5)

        self.label_7 = QLabel(GEMSRunDialog)
        self.label_7.setObjectName("label_7")
        font1 = QFont()
        font1.setFamilies(["Verdana"])
        font1.setPointSize(14)
        font1.setItalic(False)
        font1.setUnderline(False)
        self.label_7.setFont(font1)

        self.horizontalLayout_7.addWidget(self.label_7)

        self.overwrite_radioButton = QRadioButton(GEMSRunDialog)
        self.overwrite_radioButton.setObjectName("overwrite_radioButton")
        font2 = QFont()
        font2.setFamilies(["Verdana"])
        font2.setPointSize(14)
        font2.setUnderline(False)
        self.overwrite_radioButton.setFont(font2)
        self.overwrite_radioButton.setChecked(True)

        self.horizontalLayout_7.addWidget(self.overwrite_radioButton)

        self.rename_radioButton = QRadioButton(GEMSRunDialog)
        self.rename_radioButton.setObjectName("rename_radioButton")
        self.rename_radioButton.setFont(font2)

        self.horizontalLayout_7.addWidget(self.rename_radioButton)

        self.horizontalSpacer_6 = QSpacerItem(118, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer_6)

        self.gridLayout.addLayout(self.horizontalLayout_7, 5, 0, 1, 1)

        self.horizontalLayout_9 = QHBoxLayout()
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.debug_checkBox = QCheckBox(GEMSRunDialog)
        self.debug_checkBox.setObjectName("debug_checkBox")
        self.debug_checkBox.setFont(font2)
        self.debug_checkBox.setLayoutDirection(Qt.RightToLeft)
        self.debug_checkBox.setChecked(False)

        self.horizontalLayout_9.addWidget(self.debug_checkBox)

        self.horizontalSpacer_7 = QSpacerItem(348, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_9.addItem(self.horizontalSpacer_7)

        self.gridLayout.addLayout(self.horizontalLayout_9, 7, 0, 1, 1)

        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.media_checkBox = QCheckBox(GEMSRunDialog)
        self.media_checkBox.setObjectName("media_checkBox")
        self.media_checkBox.setFont(font2)
        self.media_checkBox.setLayoutDirection(Qt.RightToLeft)
        self.media_checkBox.setChecked(True)

        self.horizontalLayout_8.addWidget(self.media_checkBox)

        self.horizontalSpacer_4 = QSpacerItem(308, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_8.addItem(self.horizontalSpacer_4)

        self.gridLayout.addLayout(self.horizontalLayout_8, 6, 0, 1, 1)

        self.fn_label = QLabel(GEMSRunDialog)
        self.fn_label.setObjectName("fn_label")
        font3 = QFont()
        font3.setFamilies(["Verdana"])
        font3.setPointSize(16)
        font3.setItalic(False)
        font3.setUnderline(True)
        self.fn_label.setFont(font3)

        self.gridLayout.addWidget(self.fn_label, 2, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.horizontalSpacer_8 = QSpacerItem(138, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_8)

        self.run_pushButton = QPushButton(GEMSRunDialog)
        self.run_pushButton.setObjectName("run_pushButton")
        font4 = QFont()
        font4.setFamilies(["Verdana"])
        font4.setPointSize(16)
        font4.setBold(True)
        font4.setUnderline(False)
        self.run_pushButton.setFont(font4)
        icon = QIcon()
        icon.addFile(":/newPrefix/media/1409889607_Play.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.run_pushButton.setIcon(icon)

        self.horizontalLayout_4.addWidget(self.run_pushButton)

        self.horizontalSpacer_9 = QSpacerItem(138, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_9)

        self.gridLayout.addLayout(self.horizontalLayout_4, 8, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.save_checkBox = QCheckBox(GEMSRunDialog)
        self.save_checkBox.setObjectName("save_checkBox")
        self.save_checkBox.setFont(font2)
        self.save_checkBox.setLayoutDirection(Qt.RightToLeft)
        self.save_checkBox.setChecked(True)

        self.horizontalLayout_6.addWidget(self.save_checkBox)

        self.horizontalSpacer_3 = QSpacerItem(418, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_3)

        self.gridLayout.addLayout(self.horizontalLayout_6, 4, 0, 1, 1)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.labelAppName = QLabel(GEMSRunDialog)
        self.labelAppName.setObjectName("labelAppName")
        font5 = QFont()
        font5.setFamilies(["Verdana"])
        font5.setPointSize(20)
        font5.setBold(True)
        font5.setUnderline(False)
        self.labelAppName.setFont(font5)

        self.horizontalLayout_3.addWidget(self.labelAppName)

        self.horizontalSpacer = QSpacerItem(18, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)

        self.label_6 = QLabel(GEMSRunDialog)
        self.label_6.setObjectName("label_6")
        self.label_6.setMaximumSize(QSize(50, 50))
        font6 = QFont()
        font6.setFamilies(["Verdana"])
        font6.setPointSize(12)
        font6.setUnderline(False)
        self.label_6.setFont(font6)
        self.label_6.setPixmap(QPixmap(":/newPrefix/media/Agate-icon.png"))
        self.label_6.setScaledContents(True)

        self.horizontalLayout_3.addWidget(self.label_6)

        self.horizontalLayout.addLayout(self.horizontalLayout_3)

        self.horizontalSpacer_2 = QSpacerItem(148, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer_2)

        self.close_pushButton = QPushButton(GEMSRunDialog)
        self.close_pushButton.setObjectName("close_pushButton")
        self.close_pushButton.setMinimumSize(QSize(0, 41))
        self.close_pushButton.setFont(font2)

        self.horizontalLayout.addWidget(self.close_pushButton)

        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label = QLabel(GEMSRunDialog)
        self.label.setObjectName("label")
        font7 = QFont()
        font7.setFamilies(["Verdana"])
        font7.setPointSize(14)
        font7.setBold(False)
        font7.setUnderline(False)
        self.label.setFont(font7)
        self.label.setLayoutDirection(Qt.LeftToRight)
        self.label.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)

        self.verticalLayout_2.addWidget(self.label)

        self.verticalSpacer = QSpacerItem(20, 30, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.MinimumExpanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.label_4 = QLabel(GEMSRunDialog)
        self.label_4.setObjectName("label_4")
        self.label_4.setFont(font7)
        self.label_4.setScaledContents(False)
        self.label_4.setAlignment(Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter)
        self.label_4.setWordWrap(True)

        self.verticalLayout_2.addWidget(self.label_4)

        self.verticalSpacer_2 = QSpacerItem(20, 25, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_2)

        self.horizontalLayout_5.addLayout(self.verticalLayout_2)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.dbfile_plainTextEdit = QPlainTextEdit(GEMSRunDialog)
        self.dbfile_plainTextEdit.setObjectName("dbfile_plainTextEdit")
        self.dbfile_plainTextEdit.setEnabled(True)
        self.dbfile_plainTextEdit.setMinimumSize(QSize(0, 100))
        self.dbfile_plainTextEdit.setFont(font6)
        self.dbfile_plainTextEdit.setReadOnly(True)
        self.dbfile_plainTextEdit.setPlainText("")
        self.dbfile_plainTextEdit.setTextInteractionFlags(Qt.NoTextInteraction)

        self.horizontalLayout_12.addWidget(self.dbfile_plainTextEdit)

        self.fileselect_toolButton = QToolButton(GEMSRunDialog)
        self.fileselect_toolButton.setObjectName("fileselect_toolButton")
        self.fileselect_toolButton.setFont(font6)
        icon1 = QIcon()
        icon1.addFile(":/newPrefix/media/folder-open-icon.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.fileselect_toolButton.setIcon(icon1)

        self.horizontalLayout_12.addWidget(self.fileselect_toolButton)

        self.verticalLayout.addLayout(self.horizontalLayout_12)

        self.user_plainTextEdit = QPlainTextEdit(GEMSRunDialog)
        self.user_plainTextEdit.setObjectName("user_plainTextEdit")
        font8 = QFont()
        font8.setFamilies(["Verdana"])
        font8.setPointSize(12)
        font8.setBold(False)
        font8.setUnderline(False)
        self.user_plainTextEdit.setFont(font8)
        self.user_plainTextEdit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_plainTextEdit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.user_plainTextEdit.setPlainText("")

        self.verticalLayout.addWidget(self.user_plainTextEdit)

        self.filename_label = QLabel(GEMSRunDialog)
        self.filename_label.setObjectName("filename_label")
        font9 = QFont()
        font9.setFamilies(["Verdana"])
        font9.setPointSize(12)
        font9.setBold(True)
        font9.setItalic(False)
        font9.setUnderline(False)
        self.filename_label.setFont(font9)
        self.filename_label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)

        self.verticalLayout.addWidget(self.filename_label)

        self.horizontalLayout_5.addLayout(self.verticalLayout)

        self.gridLayout.addLayout(self.horizontalLayout_5, 3, 0, 1, 1)

        self.horizontalLayout_10.addLayout(self.gridLayout)

        self.retranslateUi(GEMSRunDialog)
        self.close_pushButton.pressed.connect(GEMSRunDialog.close)

        QMetaObject.connectSlotsByName(GEMSRunDialog)

    # setupUi

    def retranslateUi(self, GEMSRunDialog):
        GEMSRunDialog.setWindowTitle(
            QCoreApplication.translate("GEMSRunDialog", "Open Environment in GEMS Runner", None)
        )
        self.label_7.setText(QCoreApplication.translate("GEMSRunDialog", "If Data File Exists: ", None))
        # if QT_CONFIG(tooltip)
        self.overwrite_radioButton.setToolTip(
            QCoreApplication.translate("GEMSRunDialog", "Overwrite any existing data file with same filename.", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.overwrite_radioButton.setText(QCoreApplication.translate("GEMSRunDialog", "Overwrite", None))
        # if QT_CONFIG(tooltip)
        self.rename_radioButton.setToolTip(
            QCoreApplication.translate("GEMSRunDialog", "Rename data file if existing ones exist.", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.rename_radioButton.setText(QCoreApplication.translate("GEMSRunDialog", "Rename", None))
        # if QT_CONFIG(tooltip)
        self.debug_checkBox.setToolTip(
            QCoreApplication.translate(
                "GEMSRunDialog", "Primarily for printing behavioral data and gems_run errors to the terminal.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.debug_checkBox.setText(QCoreApplication.translate("GEMSRunDialog", "Enable Debug Mode:  ", None))
        # if QT_CONFIG(tooltip)
        self.media_checkBox.setToolTip(
            QCoreApplication.translate(
                "GEMSRunDialog",
                "If disabled, audio and video resources specified in the environment file.\n"
                "Useful if you don't have AVBIN installed.\n"
                "Note: Speak() actions will still play.",
                None,
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.media_checkBox.setText(QCoreApplication.translate("GEMSRunDialog", "Enable Media Playback:  ", None))
        self.fn_label.setText(QCoreApplication.translate("GEMSRunDialog", "GEMS Runner Settings", None))
        self.run_pushButton.setText(QCoreApplication.translate("GEMSRunDialog", "Launch GEMS Runner", None))
        # if QT_CONFIG(tooltip)
        self.save_checkBox.setToolTip(
            QCoreApplication.translate(
                "GEMSRunDialog", "If enabled, gems_run will save behavioral data to a data file.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        self.save_checkBox.setText(QCoreApplication.translate("GEMSRunDialog", "Save Data:  ", None))
        self.labelAppName.setText(QCoreApplication.translate("GEMSRunDialog", "GEMS Editor", None))
        self.label_6.setText("")
        self.close_pushButton.setText(QCoreApplication.translate("GEMSRunDialog", "CLOSE", None))
        self.label.setText(QCoreApplication.translate("GEMSRunDialog", "Environment\n Database File:", None))
        self.label_4.setText(QCoreApplication.translate("GEMSRunDialog", "User ID:", None))
        # if QT_CONFIG(tooltip)
        self.dbfile_plainTextEdit.setToolTip(
            QCoreApplication.translate(
                "GEMSRunDialog", "Click Folder Icon To Choose A Gems Environment Database File.", None
            )
        )
        # endif // QT_CONFIG(tooltip)
        # if QT_CONFIG(tooltip)
        self.fileselect_toolButton.setToolTip(
            QCoreApplication.translate("GEMSRunDialog", "Click To Choose A Gems Environment Database File.", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.fileselect_toolButton.setText(QCoreApplication.translate("GEMSRunDialog", "...", None))
        # if QT_CONFIG(tooltip)
        self.user_plainTextEdit.setToolTip(
            QCoreApplication.translate("GEMSRunDialog", "Specify a user id. Used to name data file.", None)
        )
        # endif // QT_CONFIG(tooltip)
        self.filename_label.setText(QCoreApplication.translate("GEMSRunDialog", "Data Filename: gemsrun.txt", None))

    # retranslateUi
