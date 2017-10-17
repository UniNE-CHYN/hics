from OpenGL.GL import *
from PyQt4 import QtGui, QtCore
from PyQt4.QtOpenGL import *
import random
import time
import numpy

class GLPlotCanvas(QGLWidget):
    _time_range = 1.
    
    def __init__(self, parent = None):
        super(GLPlotCanvas, self).__init__(parent)
        self._plots = {}
        self._timer = QtCore.QTimer(self)
        self._timer.timeout.connect(self.update)
        self._timer.start(1000./25.)
        self.setMouseTracking(True)
        
        self._axis = (0, 1, 0, 1)
        
        self._x_min = None
        self._x_max = None
        
        self._y_min = None
        self._y_max = None
        
        self._timed_value_expiration = None
        
    def leaveEvent(self, event):
        self.parent().window().statusbar.clearMessage()
        
    def mouseMoveEvent(self, event):
        x = (event.x() / self.width()) * (self._axis[1] - self._axis[0]) + self._axis[0]
        y = (1 - event.y() / self.height()) * (self._axis[3] - self._axis[2]) + self._axis[2]
        self.parent().window().statusbar.showMessage('{0}: {1:0.02f} {2:0.02f}'.format(self.parent().windowTitle(), x, y))

    def paintGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        old_keys = sorted(self._plots.keys())
        
        #No plot, abort!
        if len(old_keys) == 0:
            return
        
        keys = []
        
        for k in old_keys:
            if k < time.time() - self._time_range and k != old_keys[-1]:
                del self._plots[k]
            else:
                keys.append(k)
                
        x_min = None
        x_max = None
        y_min = None
        y_max = None
        for k in keys:
            s_x_min = min(self._plots[k][0])
            s_x_max = max(self._plots[k][0])
            s_y_min = min(self._plots[k][1])
            s_y_max = max(self._plots[k][1])
            
            if x_min is None or s_x_min < x_min:
                x_min = s_x_min
            if x_max is None or s_x_max > x_max:
                x_max = s_x_max
            if y_min is None or s_y_min < y_min:
                y_min = s_y_min
            if y_max is None or s_y_max > y_max:
                y_max = s_y_max
                
        if self._x_min is not None:
            x_min = self._x_min
        if self._x_max is not None:
            x_max = self._x_max
        if self._y_min is not None:
            y_min = self._y_min
        if self._y_max is not None:
            y_max = self._y_max
        
        self._axis = (x_min, x_max, y_min, y_max)
        
        if x_min == x_max or y_min == y_max:
            return
                    
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(x_min, x_max, y_min, y_max, -50.0, 50.0)
        glViewport(0, 0, self._width, self._height)
        
        t = time.time()
        
        for k in keys:
            if k == keys[-1]:
                factor = 1
            else:
                factor = max(0, min(1., 1. - (t - k) / self._time_range))
                
            glColor3f(factor, 0.0, 0.0)
            glBegin(GL_LINE_STRIP)
            for x, y in zip(self._plots[k][0], self._plots[k][1]):
                glVertex3f(x, y, 0)
            glEnd()

    def resizeGL(self, w, h):
        self._width = w
        self._height = h
        self.update()

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
    def update_plot(self, *args):
        if len(args) == 1:
            x_values = range(len(args[0]))
            y_values = args[0]
            style = None
        elif len(args) == 2:
            x_values = args[0]
            y_values = args[1]
            style = None
        
        k = time.time()
        self._plots[k] = (x_values, y_values, style)
        #self.update()
        
    def add_timed_value(self, value):
        if len(self._plots) == 0:
            self._plots[time.time()] = ([0.], [value], None)
        elif len(self._plots) == 1:
            base_time = list(self._plots.keys())[0]
            value_time = time.time()
            self._plots[base_time][0].append(value_time - base_time)
            self._plots[base_time][1].append(value)
            if self.timed_value_expiration is not None:
                max_time = max(self._plots[base_time][0])
                
                while max_time - self._plots[base_time][0][0] > self.timed_value_expiration:
                    self._plots[base_time][0].pop(0)
                    self._plots[base_time][1].pop(0)
                    
                #Move graph to avoid having "infinite coordinates"
                delta = self._plots[base_time][0][0]
                if delta > 0:
                    self._plots[base_time+delta] = ([x - delta for x in self._plots[base_time][0]], self._plots[base_time][1], self._plots[base_time][2])
                    del self._plots[base_time]
        else:
            assert False, "Could not add timed value if more than one data series"
            
        #self.update()
        
    @property
    def timed_value_expiration(self):
        return self._timed_value_expiration
    
    @timed_value_expiration.setter
    def timed_value_expiration(self, value):
        assert type(value) == float or value is None
        self._timed_value_expiration = value
        

    def export_data(self):
        k = sorted(self._plots.keys())[-1]
        
        data_x = self._plots[k][0]
        data_y = self._plots[k][1]
        
        if type(data_x) in (numpy.array, numpy.ndarray, numpy.ma.MaskedArray):
            data_x = data_x.tolist()
            
        if type(data_y) in (numpy.array, numpy.ndarray, numpy.ma.MaskedArray):
            data_y = data_y.tolist()
        
        d = []
        d.append('import numpy')
        d.append('')
        d.append('data_x = numpy.array({0},dtype=numpy.float)'.format(data_x))
        d.append('data_y = numpy.array({0},dtype=numpy.float)'.format(data_y))
        d.append('')
        d.append('if __name__ == \'__main__\':')
        d.append('  from matplotlib import pyplot as plt')
        d.append('  plt.plot(data_x, data_y)')
        d.append('  plt.show()')
        return '\n'.join(d)
