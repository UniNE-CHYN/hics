from PyQt5 import QtCore, QtWidgets, QtGui
from .mpl import MplCanvas
import numpy
import scipy.interpolate
import matplotlib.cm
import matplotlib.colors

class ColorCurvesWindow(QtWidgets.QDialog):
    def __init__(self, parent, hdv):
        super().__init__(parent)
        
        self._hdv = hdv
        
        self._cmmenu = QtWidgets.QMenu(self)

        
        vl = QtWidgets.QVBoxLayout(self)
        hl = QtWidgets.QHBoxLayout()
        
        bands_used = False
        for k in 'rgb':
            if self._hdv.display_bands[k] is not None:
                hl.addWidget(MplColorCurveCanvas(self, hdv, self._hdv.display_bands[k]))
                bands_used = True
                
        if not bands_used:
            hl.addWidget(MplColorCurveCanvas(self, hdv, None))
        vl.addLayout(hl)
        self._bb = QtWidgets.QDialogButtonBox(self)
        self._bb.setOrientation(QtCore.Qt.Horizontal)
        self._bb.setStandardButtons(QtWidgets.QDialogButtonBox.Close|QtWidgets.QDialogButtonBox.RestoreDefaults)
        if not bands_used:
            self._bb.addButton('Change colormap', QtWidgets.QDialogButtonBox.ActionRole)
        vl.addWidget(self._bb)

        self._bb.clicked.connect(self.buttonClicked)
        #self.buttonBox.accepted.connect(Dialog.accept)
        #self.buttonBox.rejected.connect(Dialog.reject)
        #QtCore.QMetaObject.connectSlotsByName(Dialog)
        
    def __set_cm(self, cm):
        self._hdv.cm = cm
        
    def buttonClicked(self, button):
        if self._bb.buttonRole(button) == QtWidgets.QDialogButtonBox.ResetRole:
            self._hdv.cnorm_points = {}
            
        elif self._bb.buttonRole(button) == QtWidgets.QDialogButtonBox.RejectRole:
            self.close()
        
        elif self._bb.buttonRole(button) == QtWidgets.QDialogButtonBox.ActionRole:
            #FIXME: check if the button is the one we think, but for now there is only one...
            self._cmmenu.clear()
            for cm_name in sorted(m for m in matplotlib.cm.datad):
                action = self._cmmenu.addAction(cm_name)
                action.triggered.connect(lambda x, y=cm_name: self.__set_cm(y))
                if cm_name == self._hdv.cm.name:
                    action.setCheckable(True)
                    action.setChecked(True)
                    
            self._cmmenu.exec_(QtGui.QCursor().pos())
            

class MplColorCurveCanvas(MplCanvas):
    histo_alpha = 0.5
    _rgb_cmaps = {
        'r': matplotlib.colors.LinearSegmentedColormap.from_list('_red', [(0, 0, 0), (1, 0, 0)], 256),
        'g': matplotlib.colors.LinearSegmentedColormap.from_list('_green', [(0, 0, 0), (0, 1, 0)], 256),
        'b': matplotlib.colors.LinearSegmentedColormap.from_list('_blue', [(0, 0, 0), (0, 0, 1)], 256), 
    }

    def __init__(self, parent, hdv, band_id):
        MplCanvas.__init__(self, parent, 5, 4, 100)
        self._hdv = hdv
        self._band_id = band_id
        
        data = self._hdv.data_for_band(band_id)
        self._histo = numpy.histogram(data.compressed(), 100)
        
        self._move_mutex = QtCore.QMutex(QtCore.QMutex.NonRecursive)
        
        if self._band_id is None:
            self._cmap = hdv.cm
        else:
            self._cmap = self._rgb_cmaps[[color for color, hdv_band_id in self._hdv.display_bands.items() if hdv_band_id == band_id][0]]
        
        self.mpl_connect('button_press_event', self.__mpl_onpress)
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        self.mpl_connect('motion_notify_event', self.__mpl_onmousemove)
        
        self._plots_init()
        self._plots_update()
        self._point_moving = None
        self._dragging = False
        
        hdv.display2dChanged.connect(self._plots_update)
        
    @property
    def _points(self):
        return self._hdv.cnorm_points_get(self._band_id)
    
    def _point_remove(self, point):
        d = self._hdv.cnorm_points_get(self._band_id)[:]
        d_inner = d[1:-1]
        d_inner.remove(point)
        self._hdv.cnorm_points_set(self._band_id, [d[0]]+d_inner+[d[-1]])
        
    def _point_add(self, point):
        d = self._hdv.cnorm_points_get(self._band_id)
        d.append(point)
        d.sort()
        self._hdv.cnorm_points_set(self._band_id, d)
        
        
        
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
