# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'cameraoutput.ui'
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

class Ui_CameraOutput(object):
    def setupUi(self, CameraOutput):
        CameraOutput.setObjectName(_fromUtf8("CameraOutput"))
        CameraOutput.resize(274, 338)
        self.horizontalLayout = QtGui.QHBoxLayout(CameraOutput)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lbPicture = QtGui.QLabel(CameraOutput)
        self.lbPicture.setMinimumSize(QtCore.QSize(240, 320))
        self.lbPicture.setMaximumSize(QtCore.QSize(240, 320))
        self.lbPicture.setAlignment(QtCore.Qt.AlignCenter)
        self.lbPicture.setObjectName(_fromUtf8("lbPicture"))
        self.horizontalLayout.addWidget(self.lbPicture)

        self.retranslateUi(CameraOutput)
        QtCore.QMetaObject.connectSlotsByName(CameraOutput)

    def retranslateUi(self, CameraOutput):
        CameraOutput.setWindowTitle(_translate("CameraOutput", "Camera live output", None))
        self.lbPicture.setText(_translate("CameraOutput", "[Waiting for picture]", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    CameraOutput = QtGui.QWidget()
    ui = Ui_CameraOutput()
    ui.setupUi(CameraOutput)
    CameraOutput.show()
    sys.exit(app.exec_())

