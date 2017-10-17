from PyQt4 import QtGui, QtCore
from .ui.cameraoutput import Ui_CameraOutput
import numpy
import matplotlib.cm
#from .widgets.mplcanvas import MplCanvas as PlotCanvas
from .widgets.glplotcanvas import GLPlotCanvas as PlotCanvas
import functools
import redis

class CameraOutputWindow(QtGui.QWidget, Ui_CameraOutput):
    closed = QtCore.pyqtSignal()
    resizable = False
    
    def __init__(self, *args, **kwargs):
        self._colortable = [QtGui.qRgb(*color[:3]) for color in 255*matplotlib.cm.jet(range(256))]
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        
        self.resize(self.sizeHint())
        
        self.lbPicture.setMouseTracking(True)
        self.lbPicture.mouseMoveEvent = self.picMouseMoveEvent
        self.lbPicture.mousePressEvent = self.clickedEvent
        
        self._matrix = None
        self._wavelengths = None
        self._plots = {}
        
    def closeEvent(self, event):
        self.closed.emit()
        for p in self._plots.values():
            assert isinstance(p, QtGui.QMdiSubWindow)
            p.close()
            
    def leaveEvent(self, event):
        self.parent().window().statusbar.clearMessage()
        
    def picMouseMoveEvent(self, event):
        x = event.x()
        y = event.y()
        
        if x < 0 or y < 0:
            return
            
        
        if self._wavelengths is not None:
            if x >= len(self._wavelengths):
                return
            self.parent().window().statusbar.showMessage('{0}: ω={1:0.02f}nm y={2:0.02f}'.format(self.parent().windowTitle(), self._wavelengths[x], y))
        else:
            self.parent().window().statusbar.showMessage('{0}: x={1:0.02f} y={2:0.02f}'.format(self.parent().windowTitle(), x, y))
        
    def hypcam_picture_received(self, matrix):
        self._matrix = matrix
        
        new_matrix = numpy.rollaxis(matrix * 255, 2, 1)
        new_matrix = numpy.require(new_matrix, numpy.uint8, 'C')
        
        image = QtGui.QImage(new_matrix.data, new_matrix.shape[1], new_matrix.shape[0], QtGui.QImage.Format_Indexed8)
        image.setColorTable(self._colortable)
        self.lbPicture.setFixedSize(new_matrix.shape[1], new_matrix.shape[0])
        self.lbPicture.setPixmap(QtGui.QPixmap.fromImage(image))
        
        #If we don't have wavelengths yet, then it's an opportunity to fetch them
        if self._wavelengths is None:
            redis_client = self.parent().window()._redis_client
            assert isinstance(redis_client, redis.client.Redis)            
            wavelengths = redis_client.get("hics:framegrabber:wavelengths")
            if wavelengths is not None:
                if type(wavelengths) == bytes:
                    wavelengths = wavelengths.decode('ascii')
                self._wavelengths = [float(x) for x in wavelengths.split(',')]        
        
        for k in self._plots.keys():
            self._update_plot(k)
        
    def clickedEvent(self, event):
        if self._matrix is None:
            return
        position = event.pos()
        
        if event.button() == 1:  #left click
            plot_key = 's{0}'.format(position.y())
            width = 256
            height = 256
        elif event.button() == 2: #right click
            plot_key = 'm{0}'.format(position.x())
            width = 320
            height = 256
        else:
            return
            
        if plot_key not in self._plots:
            window = self.parent().window().mdiArea.addSubWindow(PlotCanvas(self))
            window.widget()._y_min = 0
            window.widget()._y_max = 1
            window.show()
            #Default size
            window.resize(width, height)
            self._plots[plot_key] = window
            window.destroyed.connect(functools.partial(self._close_plot, plot_key))
            
        self._update_plot(plot_key)
        
    def _update_plot(self, plot_key):
        assert plot_key in self._plots
        
        window = self._plots[plot_key]
        val = int(plot_key[1:])
        
        if plot_key.startswith('s'):
            window.setWindowTitle("Spectrum plot at y={0}".format(val))
            if self._wavelengths is not None:
                window.widget().update_plot(self._wavelengths, self._matrix[val, 0, :].reshape(self._matrix.shape[2]))
            else:
                window.widget().update_plot(self._matrix[val, 0, :].reshape(self._matrix.shape[2]))
        elif plot_key.startswith('m'):
            if self._wavelengths is not None:
                window.setWindowTitle("Magnitude plot at ω={0}nm".format(self._wavelengths[val]))
            else:
                window.setWindowTitle("Magnitude plot")
            window.widget().update_plot(self._matrix[:, 0, val].reshape(self._matrix.shape[0]))                        
        
        
    def _close_plot(self, plot_key, window):
        assert self._plots[plot_key] == window
        del self._plots[plot_key]
        
    def export_data(self):
        d = []
        d.append('import numpy')
        d.append('')
        d.append('data = numpy.array({0},dtype=numpy.float)'.format(self._matrix.tolist()))
        d.append('')
        d.append('if __name__ == \'__main__\':')
        d.append('  from matplotlib import pyplot as plt')
        d.append('  plt.imshow(numpy.average(data, 1))')
        d.append('  plt.show()')
        return '\n'.join(d)
        
