# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'waterfall.ui'
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

class Ui_Waterfall(object):
    def setupUi(self, Waterfall):
        Waterfall.setObjectName(_fromUtf8("Waterfall"))
        Waterfall.resize(435, 338)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Ignored, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Waterfall.sizePolicy().hasHeightForWidth())
        Waterfall.setSizePolicy(sizePolicy)
        self.gridLayout = QtGui.QGridLayout(Waterfall)
        self.gridLayout.setMargin(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lbWaterfall = QtGui.QLabel(Waterfall)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbWaterfall.sizePolicy().hasHeightForWidth())
        self.lbWaterfall.setSizePolicy(sizePolicy)
        self.lbWaterfall.setMinimumSize(QtCore.QSize(0, 320))
        self.lbWaterfall.setMaximumSize(QtCore.QSize(16777215, 320))
        self.lbWaterfall.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.lbWaterfall.setObjectName(_fromUtf8("lbWaterfall"))
        self.gridLayout.addWidget(self.lbWaterfall, 0, 0, 1, 1)

        self.retranslateUi(Waterfall)
        QtCore.QMetaObject.connectSlotsByName(Waterfall)

    def retranslateUi(self, Waterfall):
        Waterfall.setWindowTitle(_translate("Waterfall", "Waterfall plot", None))
        self.lbWaterfall.setText(_translate("Waterfall", "[Waiting for data]", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    Waterfall = QtGui.QWidget()
    ui = Ui_Waterfall()
    ui.setupUi(Waterfall)
    Waterfall.show()
    sys.exit(app.exec_())

