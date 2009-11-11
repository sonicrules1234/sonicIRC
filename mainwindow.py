# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Python26\Lib\site-packages\PyQt4\sonicIRC\main.ui'
#
# Created: Sun Nov 08 17:13:32 2009
#      by: PyQt4 UI code generator 4.6.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
from PyQt4.QtCore import pyqtSignal, Qt
from PyQt4.QtGui import QApplication, QLineEdit, QVBoxLayout, QWidget
class LineEdit(QLineEdit):

    tabPressed = pyqtSignal()
    
    def __init__(self, parent = None):
    
        QLineEdit.__init__(self, parent)
    
    def keyPressEvent(self, event):
    
        if event.key() == Qt.Key_Control:
            self.tabPressed.emit()
            event.accept()
        else:
            QLineEdit.keyPressEvent(self, event)



class Ui_sonicIRC(object):
    def setupUi(self, sonicIRC):
        sonicIRC.setObjectName("sonicIRC")
        sonicIRC.resize(850, 565)
        self.centralwidget = QtGui.QWidget(sonicIRC)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_5 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Vertical)
        self.splitter_2.setObjectName("splitter_2")
        self.splitter = QtGui.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.listWidget = QtGui.QListWidget(self.splitter)
        self.listWidget.setObjectName("listWidget")
        self.plainTextEdit = QtGui.QPlainTextEdit(self.splitter)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.listWidget_2 = QtGui.QListWidget(self.splitter)
        self.listWidget_2.setObjectName("listWidget_2")
        self.lineEdit = LineEdit(self.splitter_2)
        self.lineEdit.setObjectName("lineEdit")
        self.gridLayout_5.addWidget(self.splitter_2, 0, 0, 1, 1)
        sonicIRC.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(sonicIRC)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 850, 21))
        self.menubar.setObjectName("menubar")
        sonicIRC.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(sonicIRC)
        self.statusbar.setObjectName("statusbar")
        sonicIRC.setStatusBar(self.statusbar)

        self.retranslateUi(sonicIRC)
        QtCore.QMetaObject.connectSlotsByName(sonicIRC)

    def retranslateUi(self, sonicIRC):
        sonicIRC.setWindowTitle(QtGui.QApplication.translate("sonicIRC", "MainWindow", None, QtGui.QApplication.UnicodeUTF8))

