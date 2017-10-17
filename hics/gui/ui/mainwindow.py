# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(466, 528)
        MainWindow.setWindowOpacity(1.0)
        MainWindow.setDocumentMode(False)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.mdiArea = QtGui.QMdiArea(self.centralwidget)
        self.mdiArea.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.mdiArea.setObjectName(_fromUtf8("mdiArea"))
        self.horizontalLayout.addWidget(self.mdiArea)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 466, 27))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Window = QtGui.QMenu(self.menubar)
        self.menu_Window.setObjectName(_fromUtf8("menu_Window"))
        self.menu_Advanced = QtGui.QMenu(self.menubar)
        self.menu_Advanced.setObjectName(_fromUtf8("menu_Advanced"))
        self.menuPlugins = QtGui.QMenu(self.menubar)
        self.menuPlugins.setObjectName(_fromUtf8("menuPlugins"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionCameraOutputShow = QtGui.QAction(MainWindow)
        self.actionCameraOutputShow.setCheckable(True)
        self.actionCameraOutputShow.setObjectName(_fromUtf8("actionCameraOutputShow"))
        self.actionMagnitudeWaterfallShow = QtGui.QAction(MainWindow)
        self.actionMagnitudeWaterfallShow.setCheckable(True)
        self.actionMagnitudeWaterfallShow.setObjectName(_fromUtf8("actionMagnitudeWaterfallShow"))
        self.actionNew_magnitude_view = QtGui.QAction(MainWindow)
        self.actionNew_magnitude_view.setObjectName(_fromUtf8("actionNew_magnitude_view"))
        self.actionFocusControlShow = QtGui.QAction(MainWindow)
        self.actionFocusControlShow.setCheckable(True)
        self.actionFocusControlShow.setObjectName(_fromUtf8("actionFocusControlShow"))
        self.actionCameraControlShow = QtGui.QAction(MainWindow)
        self.actionCameraControlShow.setCheckable(True)
        self.actionCameraControlShow.setObjectName(_fromUtf8("actionCameraControlShow"))
        self.actionScannerControlShow = QtGui.QAction(MainWindow)
        self.actionScannerControlShow.setCheckable(True)
        self.actionScannerControlShow.setObjectName(_fromUtf8("actionScannerControlShow"))
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionSettings = QtGui.QAction(MainWindow)
        self.actionSettings.setObjectName(_fromUtf8("actionSettings"))
        self.actionLocked = QtGui.QAction(MainWindow)
        self.actionLocked.setCheckable(True)
        self.actionLocked.setObjectName(_fromUtf8("actionLocked"))
        self.action_Unlock = QtGui.QAction(MainWindow)
        self.action_Unlock.setObjectName(_fromUtf8("action_Unlock"))
        self.actionSaveState = QtGui.QAction(MainWindow)
        self.actionSaveState.setObjectName(_fromUtf8("actionSaveState"))
        self.actionLoadState = QtGui.QAction(MainWindow)
        self.actionLoadState.setObjectName(_fromUtf8("actionLoadState"))
        self.actionExportData = QtGui.QAction(MainWindow)
        self.actionExportData.setObjectName(_fromUtf8("actionExportData"))
        self.menu_File.addAction(self.actionExportData)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSaveState)
        self.menu_File.addAction(self.actionLoadState)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionSettings)
        self.menu_File.addSeparator()
        self.menu_File.addAction(self.actionQuit)
        self.menu_Window.addAction(self.actionCameraControlShow)
        self.menu_Window.addAction(self.actionScannerControlShow)
        self.menu_Window.addAction(self.actionFocusControlShow)
        self.menu_Window.addSeparator()
        self.menu_Window.addAction(self.actionCameraOutputShow)
        self.menu_Window.addSeparator()
        self.menu_Window.addAction(self.actionMagnitudeWaterfallShow)
        self.menu_Advanced.addAction(self.actionLocked)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuPlugins.menuAction())
        self.menubar.addAction(self.menu_Window.menuAction())
        self.menubar.addAction(self.menu_Advanced.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "Hyper Spectral Camera Controller", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Window.setTitle(_translate("MainWindow", "&Window", None))
        self.menu_Advanced.setTitle(_translate("MainWindow", "&Advanced", None))
        self.menuPlugins.setTitle(_translate("MainWindow", "&Plugins", None))
        self.actionCameraOutputShow.setText(_translate("MainWindow", "Camera live output", None))
        self.actionMagnitudeWaterfallShow.setText(_translate("MainWindow", "Magnitude waterfall", None))
        self.actionNew_magnitude_view.setText(_translate("MainWindow", "New magnitude view", None))
        self.actionFocusControlShow.setText(_translate("MainWindow", "Focus control", None))
        self.actionCameraControlShow.setText(_translate("MainWindow", "Camera control", None))
        self.actionScannerControlShow.setText(_translate("MainWindow", "Scanner control", None))
        self.actionQuit.setText(_translate("MainWindow", "&Quit", None))
        self.actionSettings.setText(_translate("MainWindow", "&Settings...", None))
        self.actionLocked.setText(_translate("MainWindow", "&Locked", None))
        self.action_Unlock.setText(_translate("MainWindow", "&Unlock", None))
        self.actionSaveState.setText(_translate("MainWindow", "S&ave state...", None))
        self.actionLoadState.setText(_translate("MainWindow", "L&oad state...", None))
        self.actionExportData.setText(_translate("MainWindow", "&Export data...", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

