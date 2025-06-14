# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Doctor_AddPrescription.ui'
#
# Created by: PyQt5 UI code generator 5.15.11
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 311)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setMaximumSize(QtCore.QSize(16777215, 311))
        MainWindow.setBaseSize(QtCore.QSize(700, 300))
        MainWindow.setStyleSheet("*{\n"
"    padding: 0px;\n"
"    margin: 0px;\n"
"    border: 0px;\n"
"    background-color: #F4F7ED;\n"
"}\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(20, -1, 20, 10)
        self.verticalLayout.setSpacing(5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.Header = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Header.sizePolicy().hasHeightForWidth())
        self.Header.setSizePolicy(sizePolicy)
        self.Header.setStyleSheet("QLabel {\n"
"    font: bold 20pt \"Satoshi Black\";\n"
"    color: #2E6E65;\n"
"    qproperty-wordWrap: true;\n"
"    background: transparent;\n"
"    text-align: center;\n"
"}\n"
"#Subheader {\n"
"    font: 500 14pt \"Satoshi Medium\";\n"
"}")
        self.Header.setObjectName("Header")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.Header)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.Subheader = QtWidgets.QLabel(self.Header)
        self.Subheader.setAlignment(QtCore.Qt.AlignCenter)
        self.Subheader.setObjectName("Subheader")
        self.verticalLayout_2.addWidget(self.Subheader)
        self.verticalLayout.addWidget(self.Header, 0, QtCore.Qt.AlignTop)
        self.Body = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Body.sizePolicy().hasHeightForWidth())
        self.Body.setSizePolicy(sizePolicy)
        self.Body.setStyleSheet("QLabel {\n"
"    font: 300 12pt \"Lexend Light\";\n"
"    color: #2E6E65;\n"
"}\n"
"#Title_1, #Title_2, #Title_3 {\n"
"    font: 14pt \"Lexend SemiBold\";\n"
"}\n"
"#Indicator {\n"
"    font: 300 10pt \"Lexend Light\";\n"
"}\n"
"#StaffTypeCon, #StaffNameCon, #StaffInfoCon, #SpecializationCon {\n"
"    background-color: transparent;\n"
"}\n"
"*{\n"
"    background-color: transparent;\n"
"}\n"
"#Body {\n"
"    background-color: rgba(46, 110, 101, 77);\n"
"    border-radius: 15px;\n"
"}\n"
"QLineEdit, QComboBox, QDateEdit {\n"
"    background-color: #F4F7ED;\n"
"    border: 1px solid #2E6E65;\n"
"    border-radius: 10px;\n"
"}\n"
"\n"
"\n"
"QComboBox, QDateEdit {\n"
"    background-color: #F4F7ED;\n"
"    border: 1px solid #2E6E65;\n"
"    border-radius: 10px;\n"
"    padding: 5px 10px;\n"
"    font: 300 12pt \"Lexend Light\";\n"
"}\n"
"\n"
"/* Drop-down arrow styling (QComboBox only) */\n"
"QComboBox::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 30px;\n"
"    border-left: 1px solid #2E6E65;\n"
"    background-color: #D9E4DC;\n"
"    border-top-right-radius: 8px;\n"
"    border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"QComboBox::down-arrow {\n"
"    image: url(:/lucide/icons/chevron-down.svg);\n"
"    width: 20px;\n"
"    height: 20px;\n"
"}\n"
"\n"
"/* ComboBox dropdown list view */\n"
"QComboBox QAbstractItemView {\n"
"    background-color: #F4F7ED;\n"
"    selection-background-color: #CCE3D0;\n"
"    border: 1px solid #2E6E65;\n"
"    border-radius: 2px;\n"
"    outline: 0;\n"
"    font: 300 12pt \"Lexend Light\";\n"
"}\n"
"\n"
"/* ===== QDateEdit ===== */\n"
"QDateEdit {\n"
"    background-color: #F4F7ED;\n"
"    border: 1px solid #2E6E65;\n"
"    border-radius: 10px;\n"
"    padding: 5px 10px;\n"
"    font: 300 12pt \"Lexend Light\";\n"
"}\n"
"\n"
"QDateEdit::drop-down {\n"
"    subcontrol-origin: padding;\n"
"    subcontrol-position: top right;\n"
"    width: 30px;\n"
"    border-left: 1px solid #2E6E65;\n"
"    background-color: #D9E4DC;\n"
"    border-top-right-radius: 8px;\n"
"    border-bottom-right-radius: 8px;\n"
"}\n"
"\n"
"QDateEdit::down-arrow {\n"
"    image: url(:/lucide/icons/calendar.svg);\n"
"    width: 20px;\n"
"    height: 20px;\n"
"}\n"
"\n"
"\n"
"/* ===== QCalendarWidget Popup ===== */\n"
"QCalendarWidget {\n"
"    background-color: #F4F7ED;\n"
"    border: 2px solid #2E6E65;\n"
"    border-radius: 10px;\n"
"    font: 300 10pt \"Lexend Light\";\n"
"}\n"
"\n"
"/* Month & Year Navigation */\n"
"QCalendarWidget QToolButton {\n"
"    background-color: #F4F7ED;\n"
"    border: none;\n"
"    color: #2E6E65;\n"
"    font: 300 12pt \"Lexend Light\";\n"
"    padding: 5px;\n"
"    margin: 2px;\n"
"}\n"
"\n"
"QCalendarWidget QToolButton#qt_calendar_prevmonth {\n"
"    qproperty-icon: url(:/lucide/icons/chevron-left.svg);\n"
"    qproperty-iconSize: 16px;\n"
"}\n"
"\n"
"QCalendarWidget QToolButton#qt_calendar_nextmonth {\n"
"    qproperty-icon: url(:/lucide/icons/chevron-right.svg);\n"
"    qproperty-iconSize: 16px;\n"
"}\n"
"\n"
"/* Month/Year ComboBox & SpinBox */\n"
"QCalendarWidget QComboBox,\n"
"QCalendarWidget QSpinBox {\n"
"    background-color: #F4F7ED;\n"
"    border: 1px solid #2E6E65;\n"
"    border-radius: 6px;\n"
"    padding: 2px 6px;\n"
"    font: 300 11pt \"Lexend Light\";\n"
"    color: #2E6E65;\n"
"}\n"
"\n"
"/* Calendar Table (Dates & Grid) */\n"
"QCalendarWidget QTableView {\n"
"    background-color: #F4F7ED;\n"
"    border: none;\n"
"    selection-background-color: #2E6E65;\n"
"    font: 300 11pt \"Lexend Light\";\n"
"    gridline-color: #2E6E65;\n"
"}\n"
"\n"
"\n"
"")
        self.Body.setObjectName("Body")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.Body)
        self.verticalLayout_3.setContentsMargins(-1, -1, 20, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.StaffTypeCon = QtWidgets.QWidget(self.Body)
        self.StaffTypeCon.setObjectName("StaffTypeCon")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.StaffTypeCon)
        self.horizontalLayout_3.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.JoinedDate = QtWidgets.QWidget(self.StaffTypeCon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.JoinedDate.sizePolicy().hasHeightForWidth())
        self.JoinedDate.setSizePolicy(sizePolicy)
        self.JoinedDate.setMinimumSize(QtCore.QSize(0, 0))
        self.JoinedDate.setObjectName("JoinedDate")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.JoinedDate)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(1)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.label = QtWidgets.QLabel(self.JoinedDate)
        self.label.setObjectName("label")
        self.verticalLayout_4.addWidget(self.label)
        self.MedName = QtWidgets.QLineEdit(self.JoinedDate)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.MedName.sizePolicy().hasHeightForWidth())
        self.MedName.setSizePolicy(sizePolicy)
        self.MedName.setMinimumSize(QtCore.QSize(250, 35))
        self.MedName.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.MedName.setObjectName("MedName")
        self.verticalLayout_4.addWidget(self.MedName)
        self.horizontalLayout_3.addWidget(self.JoinedDate, 0, QtCore.Qt.AlignTop)
        self.verticalLayout_3.addWidget(self.StaffTypeCon, 0, QtCore.Qt.AlignTop)
        self.Title_2 = QtWidgets.QLabel(self.Body)
        self.Title_2.setObjectName("Title_2")
        self.verticalLayout_3.addWidget(self.Title_2)
        self.frame_2 = QtWidgets.QFrame(self.Body)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout(self.frame_2)
        self.horizontalLayout_5.setContentsMargins(10, 0, 0, 0)
        self.horizontalLayout_5.setSpacing(6)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.frame_3 = QtWidgets.QFrame(self.frame_2)
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.frame_3)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.label_2 = QtWidgets.QLabel(self.frame_3)
        self.label_2.setObjectName("label_2")
        self.verticalLayout_5.addWidget(self.label_2)
        self.Dosage = QtWidgets.QLineEdit(self.frame_3)
        self.Dosage.setMinimumSize(QtCore.QSize(0, 35))
        self.Dosage.setMaximumSize(QtCore.QSize(16777215, 35))
        self.Dosage.setObjectName("Dosage")
        self.verticalLayout_5.addWidget(self.Dosage)
        self.horizontalLayout_5.addWidget(self.frame_3)
        self.frame_4 = QtWidgets.QFrame(self.frame_2)
        self.frame_4.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_4.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_4.setObjectName("frame_4")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.frame_4)
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.label_3 = QtWidgets.QLabel(self.frame_4)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_6.addWidget(self.label_3)
        self.Intake = QtWidgets.QLineEdit(self.frame_4)
        self.Intake.setMinimumSize(QtCore.QSize(0, 35))
        self.Intake.setMaximumSize(QtCore.QSize(16777215, 35))
        self.Intake.setObjectName("Intake")
        self.verticalLayout_6.addWidget(self.Intake)
        self.horizontalLayout_5.addWidget(self.frame_4)
        self.frame_5 = QtWidgets.QFrame(self.frame_2)
        self.frame_5.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_5.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_5.setObjectName("frame_5")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.frame_5)
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.label_4 = QtWidgets.QLabel(self.frame_5)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_7.addWidget(self.label_4)
        self.Tablets = QtWidgets.QLineEdit(self.frame_5)
        self.Tablets.setMinimumSize(QtCore.QSize(0, 35))
        self.Tablets.setMaximumSize(QtCore.QSize(16777215, 35))
        self.Tablets.setObjectName("Tablets")
        self.verticalLayout_7.addWidget(self.Tablets)
        self.horizontalLayout_5.addWidget(self.frame_5)
        self.verticalLayout_3.addWidget(self.frame_2)
        self.Specialization = QtWidgets.QWidget(self.Body)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Maximum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Specialization.sizePolicy().hasHeightForWidth())
        self.Specialization.setSizePolicy(sizePolicy)
        self.Specialization.setObjectName("Specialization")
        self.verticalLayout_8 = QtWidgets.QVBoxLayout(self.Specialization)
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 10)
        self.verticalLayout_8.setSpacing(5)
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.verticalLayout_3.addWidget(self.Specialization)
        self.verticalLayout.addWidget(self.Body)
        self.Buttons = QtWidgets.QWidget(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Buttons.sizePolicy().hasHeightForWidth())
        self.Buttons.setSizePolicy(sizePolicy)
        self.Buttons.setObjectName("Buttons")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.Buttons)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.widget = QtWidgets.QWidget(self.Buttons)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy)
        self.widget.setMaximumSize(QtCore.QSize(500, 16777215))
        self.widget.setObjectName("widget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setSpacing(10)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.Cancel = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Cancel.sizePolicy().hasHeightForWidth())
        self.Cancel.setSizePolicy(sizePolicy)
        self.Cancel.setMinimumSize(QtCore.QSize(200, 45))
        self.Cancel.setMaximumSize(QtCore.QSize(200, 45))
        self.Cancel.setStyleSheet("QPushButton {\n"
"    font: 900 10pt \"Satoshi Black\";\n"
"    background-color:  #2E6E65;\n"
"    border-radius: 10px;\n"
"    font-weight: bold;\n"
"    font-size: 20px;\n"
"    color: #F4F7ED;\n"
"    text-align: center;\n"
"}")
        self.Cancel.setObjectName("Cancel")
        self.horizontalLayout_2.addWidget(self.Cancel)
        self.Addprescription = QtWidgets.QPushButton(self.widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Addprescription.sizePolicy().hasHeightForWidth())
        self.Addprescription.setSizePolicy(sizePolicy)
        self.Addprescription.setMinimumSize(QtCore.QSize(200, 45))
        self.Addprescription.setMaximumSize(QtCore.QSize(200, 45))
        self.Addprescription.setStyleSheet("QPushButton {\n"
"    font: 900 10pt \"Satoshi Black\";\n"
"    background-color:  #2E6E65;\n"
"    border-radius: 10px;\n"
"    font-weight: bold;\n"
"    font-size: 20px;\n"
"    color: #F4F7ED;\n"
"    text-align: center;\n"
"}")
        self.Addprescription.setObjectName("Addprescription")
        self.horizontalLayout_2.addWidget(self.Addprescription)
        self.horizontalLayout.addWidget(self.widget, 0, QtCore.Qt.AlignRight)
        self.verticalLayout.addWidget(self.Buttons)
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Subheader.setText(_translate("MainWindow", "Prescription Details"))
        self.label.setText(_translate("MainWindow", "Medication Name"))
        self.Title_2.setText(_translate("MainWindow", "Dosage Details"))
        self.label_2.setText(_translate("MainWindow", "Dosage"))
        self.label_3.setText(_translate("MainWindow", "Intake"))
        self.label_4.setText(_translate("MainWindow", "No. of Tablets"))
        self.Cancel.setText(_translate("MainWindow", "Cancel"))
        self.Addprescription.setText(_translate("MainWindow", "Add Prescription"))
