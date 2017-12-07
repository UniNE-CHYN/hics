# embedding_in_qt5.py --- Simple Qt5 application embedding matplotlib canvases
#
# Copyright (C) 2005 Florent Rougon
#               2006 Darren Dale
#               2015 Jens H Nielsen
#
# This file is an example program for matplotlib. It may be used and
# modified with no restriction; raw copies as well as modified versions
# may be distributed without limitation.

from __future__ import unicode_literals
import sys
import os
import random
import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

import numpy
from numpy import arange, sin, pi
import scipy.interpolate
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        
        self._move_mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        
        #self._points = [(-203, 0), (500, 150), (1000, 50),  (2134, 255)]
        self._points = []
        
        self.mpl_connect('button_press_event', self.__mpl_onpress)
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        self.mpl_connect('motion_notify_event', self.__mpl_onmousemove)
        
        self._plots_init()
        self._plots_update()
        self._point_moving = None
        self._dragging = False
        self.figure.tight_layout()
        
    @property
    def _click_distance(self):
        xl, yl = self.axes.get_xlim(), self.axes.get_ylim()
        return numpy.sqrt((yl[1]-yl[0]) **2+(xl[1]-xl[0]) **2) / 10
        
        
    def __mpl_onmousemove(self, event):
        if event.button != 1 or event.xdata is None or event.ydata is None:
            return
        
        self._dragging = True
        
        self._move_mutex.lock()
        if self._point_moving is not None:
            self._points.remove(self._point_moving)
        self._point_moving = event.xdata, event.ydata
        self._points.append(self._point_moving)
        self._move_mutex.unlock()
        self._plots_update()
        
    def _find_nearest_point(self, xdata, ydata):
        point = None
        delta = None
        for x, y in self._points:
            this_delta = numpy.sqrt((xdata-x) **2+(ydata-y) **2)
            if delta is None or this_delta < delta:
                point = x, y
                delta = this_delta
                
        xl, yl = self.axes.get_xlim(), self.axes.get_ylim()
        if point is not None and delta > self._click_distance:
            point = None
            
        return point
        
        
    def __mpl_onpress(self, event):
        if event.xdata is None or event.ydata is None:
            return
        point = self._find_nearest_point(event.xdata, event.ydata)
        if event.button == 1:
            #Add point
            self._move_mutex.lock()
            self._point_moving = point
            self._move_mutex.unlock()
        elif event.button == 3:
            if point is not None:
                self._points.remove(point)
        else:
            print('%s click: button=%d, x=%d, y=%d, xdata=%f, ydata=%f' %
              ('double' if event.dblclick else 'single', event.button,
               event.x, event.y, event.xdata, event.ydata))
    
        self._plots_update()
        
    def __mpl_onrelease(self, event):
        if event.button != 1:
            return
        if not self._dragging and (event.xdata is not None and event.ydata is not None):
            #We didn't drag at all, just add point
            self._points.append((event.xdata, event.ydata))
            self._plots_update()
        self._point_moving = None
        self._dragging = False
        
    def _plots_init(self):
        self._point_plot, = self.axes.plot([0], [0], 'ob')
        self._interpolation_plot, = self.axes.plot([0], [0], '-b')
        
    def _plots_update(self):
        self._points.sort()
        oldx = None
        for x, y in self._points[:]:
            if oldx == x:
                self._points.remove((x, y))
            oldx = x
        
        xi = [x[0] for x in self._points]
        yi = [x[1] for x in self._points]     
            
        self._point_plot.set_data(xi, yi)
        
        if len(xi) >= 2:
            xs = numpy.linspace(xi[0], xi[-1], 1000)
            ys = scipy.interpolate.pchip_interpolate(xi, yi, xs)
            self._interpolation_plot.set_data(xs, ys)
            
        if len(xi) >= 2:
            self.axes.set_xlim(min(xi), max(xi))
            self.axes.set_ylim(min(yi), max(yi))
        else:
            self.axes.set_xlim(0, 100)
            self.axes.set_ylim(0, 100)
            
        self.draw()
             
    

    def compute_initial_figure(self):
        self.axes.set_xlim(-203, 2134)
        self.axes.set_ylim(0, 255)
        

        self.axes.plot(xi, yi, 'ob')
        
        
        
        pass

class MyColorCurveCanvas(MyMplCanvas):
    pass

class MyDynamicMplCanvas(MyMplCanvas):
    """A canvas that updates itself every second with a new plot."""

    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.update_figure)
        timer.start(1000)

    def compute_initial_figure(self):
        self.axes.plot([0, 1, 2, 3], [1, 2, 0, 4], 'r')

    def update_figure(self):
        # Build a list of 4 random integers between 0 and 10 (both inclusive)
        l = [random.randint(0, 10) for i in range(4)]
        self.axes.cla()
        self.axes.plot([0, 1, 2, 3], l, 'r')
        self.draw()


class ApplicationWindow(QtWidgets.QMainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("application main window")

        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit,
                                 QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)

        self.help_menu = QtWidgets.QMenu('&Help', self)
        self.menuBar().addSeparator()
        self.menuBar().addMenu(self.help_menu)

        self.help_menu.addAction('&About', self.about)

        self.main_widget = QtWidgets.QWidget(self)

        l = QtWidgets.QVBoxLayout(self.main_widget)
        cc = MyColorCurveCanvas(self.main_widget, width=5, height=4, dpi=100)
        l.addWidget(cc)

        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)

        self.statusBar().showMessage("All hail matplotlib!", 2000)

    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

    def about(self):
        QtWidgets.QMessageBox.about(self, "About",
                                    """embedding_in_qt5.py example
Copyright 2005 Florent Rougon, 2006 Darren Dale, 2015 Jens H Nielsen

This program is a simple example of a Qt5 application embedding matplotlib
canvases.

It may be used and modified with no restriction; raw copies as well as
modified versions may be distributed without limitation.

This is modified from the embedding in qt4 example to show the difference
between qt4 and qt5"""
                                )

if False:
    
    qApp = QtWidgets.QApplication(sys.argv)
    
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    #qApp.exec_()


if __name__ == '__main__':
    from hics.viewer.mplcolorcurve import MplColorCurveCanvas
    import matplotlib.cm
    
    class ApplicationWindow(QtWidgets.QMainWindow):
        def __init__(self):
            QtWidgets.QMainWindow.__init__(self)
            self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
            self.setWindowTitle("application main window")
    
            self.file_menu = QtWidgets.QMenu('&File', self)
            self.file_menu.addAction('&Quit', self.fileQuit,
                                     QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
            self.menuBar().addMenu(self.file_menu)
    
            self.help_menu = QtWidgets.QMenu('&Help', self)
            self.menuBar().addSeparator()
            self.menuBar().addMenu(self.help_menu)
    
            self.main_widget = QtWidgets.QWidget(self)
    
            import numpy
            data = numpy.random.rand(10000)
            histdata = numpy.histogram(data, 100)
    
            l = QtWidgets.QVBoxLayout(self.main_widget)
            cc = MplColorCurveCanvas(self.main_widget, histo=histdata, cmap= matplotlib.cm.get_cmap('jet'))
            l.addWidget(cc)
    
            self.main_widget.setFocus()
            self.setCentralWidget(self.main_widget)
    
            self.statusBar().showMessage("All hail matplotlib!", 2000)
    
        def fileQuit(self):
            self.close()
    
        def closeEvent(self, ce):
            self.fileQuit()

    qApp = QtWidgets.QApplication(sys.argv)
    
    aw = ApplicationWindow()
    aw.setWindowTitle("%s" % progname)
    aw.show()
    sys.exit(qApp.exec_())
    #qApp.exec_()
    
