# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camera.ui'
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

class Ui_Camera(object):
    def setupUi(self, Camera):
        Camera.setObjectName(_fromUtf8("Camera"))
        Camera.resize(400, 161)
        self.gridLayout = QtGui.QGridLayout(Camera)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(Camera)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.sbIntegrationTime = QtGui.QDoubleSpinBox(Camera)
        self.sbIntegrationTime.setSuffix(_fromUtf8(""))
        self.sbIntegrationTime.setDecimals(1)
        self.sbIntegrationTime.setMinimum(1.0)
        self.sbIntegrationTime.setMaximum(26214.0)
        self.sbIntegrationTime.setProperty("value", 2600.0)
        self.sbIntegrationTime.setObjectName(_fromUtf8("sbIntegrationTime"))
        self.gridLayout.addWidget(self.sbIntegrationTime, 1, 1, 1, 1)
        self.label_3 = QtGui.QLabel(Camera)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.sbNuc = QtGui.QSpinBox(Camera)
        self.sbNuc.setMaximum(3)
        self.sbNuc.setObjectName(_fromUtf8("sbNuc"))
        self.gridLayout.addWidget(self.sbNuc, 2, 1, 1, 1)
        self.sbFrameRate = QtGui.QSpinBox(Camera)
        self.sbFrameRate.setMinimum(3)
        self.sbFrameRate.setMaximum(100)
        self.sbFrameRate.setObjectName(_fromUtf8("sbFrameRate"))
        self.gridLayout.addWidget(self.sbFrameRate, 0, 1, 1, 1)
        self.label_2 = QtGui.QLabel(Camera)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Camera)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)
        self.cbShutterOpen = QtGui.QCheckBox(Camera)
        self.cbShutterOpen.setChecked(True)
        self.cbShutterOpen.setObjectName(_fromUtf8("cbShutterOpen"))
        self.gridLayout.addWidget(self.cbShutterOpen, 3, 1, 1, 1)

        self.retranslateUi(Camera)
        QtCore.QMetaObject.connectSlotsByName(Camera)

    def retranslateUi(self, Camera):
        Camera.setWindowTitle(_translate("Camera", "Camera", None))
        self.label.setText(_translate("Camera", "Frame rate (fps):", None))
        self.label_3.setText(_translate("Camera", "NUC:", None))
        self.label_2.setText(_translate("Camera", "Integration time (μs):", None))
        self.label_4.setText(_translate("Camera", "Shutter:", None))
        self.cbShutterOpen.setText(_translate("Camera", "Open", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Camera = QtGui.QWidget()
    ui = Ui_Camera()
    ui.setupUi(Camera)
    Camera.show()
    sys.exit(app.exec_())

