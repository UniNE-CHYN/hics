from PyQt4 import QtGui, QtCore
import numpy

from .ui.webcamoutput import Ui_WebcamOutput

class WebcamOutputWindow(QtGui.QWidget, Ui_WebcamOutput):
    closed = QtCore.pyqtSignal()
    resizable = True
    
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        
    def closeEvent(self, event):
        self.closed.emit()
        
    def webcam_picture_received(self, matrix):
        self._matrix = matrix
        matrix = numpy.require(matrix, numpy.uint8, 'C')
        image = QtGui.QImage(matrix.data, matrix.shape[1], matrix.shape[0], QtGui.QImage.Format_RGB888)
        self.scrollAreaWidgetContents.setFixedSize(matrix.shape[1], matrix.shape[0])
        self.lbPicture.setFixedSize(matrix.shape[1], matrix.shape[0])
        self.lbPicture.setPixmap(QtGui.QPixmap.fromImage(image))
        
    def export_data(self):
        d = []
        d.append('import numpy')
        d.append('')
        d.append('data = numpy.array({0})'.format(self._matrix.tolist()))
        d.append('')
        d.append('if __name__ == \'__main__\':')
        d.append('  from matplotlib import pyplot as plt')
        d.append('  plt.imshow(numpy.average(data, 2))')
        d.append('  plt.show()')
        return '\n'.join(d)
