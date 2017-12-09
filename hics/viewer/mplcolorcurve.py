from PyQt5 import QtCore
from .mpl import MplCanvas
import numpy
import scipy.interpolate

class MplColorCurveCanvas(MplCanvas):
    histo_alpha = 0.5

    def __init__(self, parent=None, histo=None, cmap=None, width=5, height=4, dpi=100):
        MplCanvas.__init__(self, parent, width, height, dpi)
        
        self._move_mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)
        self._points = []
        self._histo = histo
        self._cmap = cmap
        
        self.mpl_connect('button_press_event', self.__mpl_onpress)
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        self.mpl_connect('motion_notify_event', self.__mpl_onmousemove)
        
        self._plots_init()
        self._plots_update()
        self._point_moving = None
        self._dragging = False
        
        
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
        hist, bins = self._histo
        width = 0.7 * (bins[1] - bins[0])
        center = (bins[:-1] + bins[1:]) / 2
        self._histobars = self.axes.bar(center, hist/numpy.max(hist), align='center', width=width)
        
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
        
        if self._histo is not None:
            xi.insert(0, self._histo[1].min())
            xi.append(self._histo[1].max())
            yi.insert(0, 0)
            yi.append(1)
            
        self._point_plot.set_data(xi, yi)
        
        if len(xi) >= 2:
            xs = numpy.linspace(xi[0], xi[-1], 1000)
            ys = scipy.interpolate.pchip_interpolate(xi, yi, xs)
            self._interpolation_plot.set_data(xs, ys)
            
        if len(xi) >= 2:
            self.axes.set_xlim(min(xi), max(xi))
            self.axes.set_ylim(min(yi), max(yi))
        else:
            self.axes.set_xlim(0, 1)
            self.axes.set_ylim(0, 1)
            
        if self._histo is not None and self._cmap is not None:
            hist, bins = self._histo
            centers = (bins[:-1] + bins[1:]) / 2
            
            #static from_list(name, colors, N=256, gamma=1.0)
            centers_values = numpy.clip(scipy.interpolate.pchip_interpolate(xi, yi, centers), 0, 1)
            for b_id, c in enumerate(centers_values):
                self._histobars[b_id].set_color(self._cmap(c, self.histo_alpha))
        self.draw()
