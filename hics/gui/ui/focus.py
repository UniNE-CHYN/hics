# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'focus.ui'
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

class Ui_Focus(object):
    def setupUi(self, Focus):
        Focus.setObjectName(_fromUtf8("Focus"))
        Focus.resize(381, 76)
        self.gridLayout = QtGui.QGridLayout(Focus)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbPosition = QtGui.QLabel(Focus)
        self.lbPosition.setObjectName(_fromUtf8("lbPosition"))
        self.gridLayout.addWidget(self.lbPosition, 1, 3, 1, 1)
        self.label = QtGui.QLabel(Focus)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.sbTo = QtGui.QSpinBox(Focus)
        self.sbTo.setMinimum(-4096000)
        self.sbTo.setMaximum(4096000)
        self.sbTo.setSingleStep(1000)
        self.sbTo.setProperty("value", 4096000)
        self.sbTo.setObjectName(_fromUtf8("sbTo"))
        self.gridLayout.addWidget(self.sbTo, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(Focus)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.sbFrom = QtGui.QSpinBox(Focus)
        self.sbFrom.setMinimum(-4096000)
        self.sbFrom.setMaximum(4096000)
        self.sbFrom.setSingleStep(1000)
        self.sbFrom.setObjectName(_fromUtf8("sbFrom"))
        self.gridLayout.addWidget(self.sbFrom, 0, 1, 1, 1)
        self.slPosition = QtGui.QSlider(Focus)
        self.slPosition.setMinimum(0)
        self.slPosition.setMaximum(4096000)
        self.slPosition.setSingleStep(1000)
        self.slPosition.setPageStep(10000)
        self.slPosition.setProperty("value", 1234567)
        self.slPosition.setTracking(False)
        self.slPosition.setOrientation(QtCore.Qt.Horizontal)
        self.slPosition.setObjectName(_fromUtf8("slPosition"))
        self.gridLayout.addWidget(self.slPosition, 1, 1, 1, 2)

        self.retranslateUi(Focus)
        QtCore.QMetaObject.connectSlotsByName(Focus)

    def retranslateUi(self, Focus):
        Focus.setWindowTitle(_translate("Focus", "Focus", None))
        self.lbPosition.setText(_translate("Focus", "1234567", None))
        self.label.setText(_translate("Focus", "Range:", None))
        self.label_2.setText(_translate("Focus", "Position:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Focus = QtGui.QWidget()
    ui = Ui_Focus()
    ui.setupUi(Focus)
    Focus.show()
    sys.exit(app.exec_())

