from PyQt4 import QtGui, QtCore
import numpy

from .ui.settings import Ui_diSettings

class SettingsWindow(QtGui.QDialog, Ui_diSettings):
    def __init__(self, *args, **kwargs):
        QtGui.QDialog.__init__(self, *args, **kwargs)
        self.setupUi(self)
        
        self._settings = QtCore.QSettings()
        self.leRedisURL.setText(self._settings.value('redis/url', 'redis://localhost'))
        
    def accept(self):
        self._settings.setValue('redis/url', self.leRedisURL.text())
        self.close()
    
