from PyQt4 import QtGui, QtCore
import random
import time
import numpy

class ProgressWidget(QtGui.QWidget):
    def __init__(self, parent=None, f=QtCore.Qt.WindowFlags()):
        QtGui.QWidget.__init__(self, parent, f)

        self.verticalLayout = QtGui.QVBoxLayout(self)
        self.pbPercentage = QtGui.QProgressBar(self)
        self.pbPercentage.setRange(0, 100)
        self.pbPercentage.setValue(0)
        self.verticalLayout.addWidget(self.pbPercentage)
        
        self.lblStatus = QtGui.QLabel(self)
        self.verticalLayout.addWidget(self.lblStatus)
        
        QtCore.QMetaObject.connectSlotsByName(self)
        
    @property
    def text(self):
        return self.lblStatus.text
    
    @text.setter
    def text(self, newvalue):
        self.lblStatus.setText(newvalue)
        self.lblStatus.repaint()
        
    @property
    def percentage(self):
        return self.pbPercentage.value
    
    @percentage.setter
    def percentage(self, newvalue):
        self.pbPercentage.setValue(int(newvalue))
        self.pbPercentage.repaint()
