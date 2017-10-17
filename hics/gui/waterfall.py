from PyQt4 import QtGui, QtCore
from .ui.waterfall import Ui_Waterfall
import numpy
import matplotlib.cm
#from .widgets.mplcanvas import MplCanvas as PlotCanvas
from .widgets.glplotcanvas import GLPlotCanvas as PlotCanvas
import functools
import redis

class WaterfallWindow(QtGui.QWidget, Ui_Waterfall):
    closed = QtCore.pyqtSignal()
    resizable = True
    
    def __init__(self, *args, **kwargs):
        self._colortable = [QtGui.qRgb(*color[:3]) for color in 255*matplotlib.cm.jet(range(256))]
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        
        self._matrix = None
        
        self.resize(self.sizeHint())
        
    def closeEvent(self, event):
        self.closed.emit()
            
    def leaveEvent(self, event):
        self.parent().window().statusbar.clearMessage()
        
    def hypcam_picture_received(self, matrix):
        data = numpy.require(numpy.ma.mean(matrix, 2) * 255, numpy.uint8, 'C')
        
        if self._matrix is None:
            self._matrix = data
        else:
            self._matrix = numpy.concatenate((data, self._matrix), 1)
            
        self._matrix = self._matrix[:, :self.lbWaterfall.width()]
        
        width, height = self._matrix.shape[1], self._matrix.shape[0]
        
        data_width = width
        #Each scanline must be 32-bit aligned!
        if (width % 4) != 0:
            _matrix_padded = numpy.pad(self._matrix, ((0, 0), (0, 4 - (width % 4))), 'constant')
        else:
            _matrix_padded = self._matrix
        _matrix_padded = numpy.require(_matrix_padded, numpy.uint8, 'C')
            
        image = QtGui.QImage(_matrix_padded.data, width, height, QtGui.QImage.Format_Indexed8)
        image.setColorTable(self._colortable)
        self.lbWaterfall.setPixmap(QtGui.QPixmap.fromImage(image))
        self.lbWaterfall.setMinimumHeight(height)
        self.lbWaterfall.setMaximumHeight(height)
        
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed)
        self.parent().setSizePolicy(sizePolicy)                
