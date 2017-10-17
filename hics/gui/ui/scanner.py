# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'scanner.ui'
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

class Ui_Scanner(object):
    def setupUi(self, Scanner):
        Scanner.setObjectName(_fromUtf8("Scanner"))
        Scanner.resize(381, 135)
        self.gridLayout = QtGui.QGridLayout(Scanner)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.sbSpeed = QtGui.QSpinBox(Scanner)
        self.sbSpeed.setMinimum(1)
        self.sbSpeed.setMaximum(100000)
        self.sbSpeed.setSingleStep(1000)
        self.sbSpeed.setObjectName(_fromUtf8("sbSpeed"))
        self.gridLayout.addWidget(self.sbSpeed, 2, 1, 1, 2)
        self.lbPosition = QtGui.QLabel(Scanner)
        self.lbPosition.setObjectName(_fromUtf8("lbPosition"))
        self.gridLayout.addWidget(self.lbPosition, 1, 3, 1, 1)
        self.label = QtGui.QLabel(Scanner)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.sbTo = QtGui.QSpinBox(Scanner)
        self.sbTo.setMinimum(-4096000)
        self.sbTo.setMaximum(4096000)
        self.sbTo.setSingleStep(1000)
        self.sbTo.setProperty("value", 4096000)
        self.sbTo.setObjectName(_fromUtf8("sbTo"))
        self.gridLayout.addWidget(self.sbTo, 0, 2, 1, 1)
        self.label_2 = QtGui.QLabel(Scanner)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.label_4 = QtGui.QLabel(Scanner)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 2, 0, 1, 1)
        self.sbFrom = QtGui.QSpinBox(Scanner)
        self.sbFrom.setMinimum(-4096000)
        self.sbFrom.setMaximum(4096000)
        self.sbFrom.setSingleStep(1000)
        self.sbFrom.setObjectName(_fromUtf8("sbFrom"))
        self.gridLayout.addWidget(self.sbFrom, 0, 1, 1, 1)
        self.slPosition = QtGui.QSlider(Scanner)
        self.slPosition.setMinimum(0)
        self.slPosition.setMaximum(4096000)
        self.slPosition.setSingleStep(1000)
        self.slPosition.setPageStep(10000)
        self.slPosition.setProperty("value", 1234567)
        self.slPosition.setTracking(False)
        self.slPosition.setOrientation(QtCore.Qt.Horizontal)
        self.slPosition.setObjectName(_fromUtf8("slPosition"))
        self.gridLayout.addWidget(self.slPosition, 1, 1, 1, 2)

        self.retranslateUi(Scanner)
        QtCore.QMetaObject.connectSlotsByName(Scanner)

    def retranslateUi(self, Scanner):
        Scanner.setWindowTitle(_translate("Scanner", "Scanner", None))
        self.lbPosition.setText(_translate("Scanner", "1234567", None))
        self.label.setText(_translate("Scanner", "Range:", None))
        self.label_2.setText(_translate("Scanner", "Position:", None))
        self.label_4.setText(_translate("Scanner", "Speed:", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Scanner = QtGui.QWidget()
    ui = Ui_Scanner()
    ui.setupUi(Scanner)
    Scanner.show()
    sys.exit(app.exec_())

