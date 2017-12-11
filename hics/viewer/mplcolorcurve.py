from PyQt5 import QtCore, QtWidgets
from .mpl import MplCanvas
import numpy
import scipy.interpolate
import matplotlib.cm
import matplotlib.colors

class ColorCurvesWindow(QtWidgets.QDialog):
    def __init__(self, parent, hdv):
        super().__init__(parent)
        
        self._hdv = hdv
        
        vl = QtWidgets.QVBoxLayout(self)
        hl = QtWidgets.QHBoxLayout()
        hl.addWidget(MplColorCurveCanvas(self, hdv, 0))
        
        if hdv.data_to_display.ndim == 3:
            for i in range(1, hdv.data_to_display.shape[2]):
                hl.addWidget(MplColorCurveCanvas(self, hdv, i))
        vl.addLayout(hl)
        self._bb = QtWidgets.QDialogButtonBox(self)
        self._bb.setOrientation(QtCore.Qt.Horizontal)
        self._bb.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.RestoreDefaults)
        vl.addWidget(self._bb)

        self._bb.clicked.connect(self.buttonClicked)
        #self.buttonBox.accepted.connect(Dialog.accept)
        #self.buttonBox.rejected.connect(Dialog.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        
    def buttonClicked(self, button):
        if self._bb.buttonRole(button) == QtWidgets.QDialogButtonBox.ResetRole:
            #restore defaults
            self._hdv.set_normpoints(0, [])
            
            if self._hdv.data_to_display.ndim == 3:
                for i in range(1, self._hdv.data_to_display.shape[2]):
                    self._hdv.set_normpoints(i, [])
        elif self._bb.buttonRole(button) == QtWidgets.QDialogButtonBox.RejectRole:
            self.close()

class MplColorCurveCanvas(MplCanvas):
    histo_alpha = 0.5
    _rgb_cmaps = [
        matplotlib.colors.LinearSegmentedColormap.from_list('_red', [(0, 0, 0), (1, 0, 0)], 256),
        matplotlib.colors.LinearSegmentedColormap.from_list('_green', [(0, 0, 0), (0, 1, 0)], 256),
        matplotlib.colors.LinearSegmentedColormap.from_list('_blue', [(0, 0, 0), (0, 0, 1)], 256), 
    ]

    def __init__(self, parent, hdv, dim_id):
        MplCanvas.__init__(self, parent, 5, 4, 100)
        self._hdv = hdv
        self._dim_id = dim_id
        
        if hdv.data_to_display.ndim == 2:
            d = hdv.data_to_display
        else:
            d = hdv.data_to_display[:, :, self._dim_id]
            
        if hasattr(d, 'compressed'):
            self._histo = numpy.histogram(d.compressed(), 100)
        else:
            self._histo = numpy.histogram(d.flatten(), 100)
        
        self._move_mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)
        
        if hdv.data_to_display.ndim == 2 or (hdv.data_to_display.ndim == 3 and hdv.data_to_display.shape[2] == 1):
            self._cmap = hdv.cm
        else:
            self._cmap = self._rgb_cmaps[self._dim_id]
        
        self.mpl_connect('button_press_event', self.__mpl_onpress)
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        self.mpl_connect('motion_notify_event', self.__mpl_onmousemove)
        
        self._plots_init()
        self._plots_update()
        self._point_moving = None
        self._dragging = False
        
        hdv.viewChanged.connect(self._plots_update)
        
    @property
    def _points(self):
        return self._hdv.get_normpoints(self._dim_id)
    
    def _point_remove(self, point):
        d = self._hdv.get_normpoints(self._dim_id)[:]
        d_inner = d[1:-1]
        d_inner.remove(point)
        self._hdv.set_normpoints(self._dim_id, [d[0]]+d_inner+[d[-1]])
        
    def _point_add(self, point):
        d = self._hdv.get_normpoints(self._dim_id)[:]
        d.append(point)
        d.sort()
        self._hdv.set_normpoints(self._dim_id, d)
        
        
        
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
            self._point_remove(self._point_moving)
        self._point_moving = event.xdata, event.ydata
        self._point_add(self._point_moving)
        self._move_mutex.unlock()
        self._plots_update()
        
    def _find_nearest_point(self, xdata, ydata):
        point = None
        delta = None
        for x, y in self._points[1:-1]:
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
                self._point_remove(point)
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
            self._point_add((event.xdata, event.ydata))
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
        oldx = None
        pts = self._points[:]
        for x, y in pts:
            if oldx == x:
                pts.remove((x, y))
            oldx = x
        
        xi = [x[0] for x in pts]
        yi = [x[1] for x in pts]
            
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
