# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
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

class Ui_diSettings(object):
    def setupUi(self, diSettings):
        diSettings.setObjectName(_fromUtf8("diSettings"))
        diSettings.resize(400, 70)
        self.formLayout = QtGui.QFormLayout(diSettings)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(diSettings)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.buttonBox = QtGui.QDialogButtonBox(diSettings)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.buttonBox)
        self.leRedisURL = QtGui.QLineEdit(diSettings)
        self.leRedisURL.setObjectName(_fromUtf8("leRedisURL"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.leRedisURL)

        self.retranslateUi(diSettings)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), diSettings.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), diSettings.reject)
        QtCore.QMetaObject.connectSlotsByName(diSettings)

    def retranslateUi(self, diSettings):
        diSettings.setWindowTitle(_translate("diSettings", "Settings", None))
        self.label.setText(_translate("diSettings", "Redis URL (restart required):", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    diSettings = QtGui.QDialog()
    ui = Ui_diSettings()
    ui.setupUi(diSettings)
    diSettings.show()
    sys.exit(app.exec_())

