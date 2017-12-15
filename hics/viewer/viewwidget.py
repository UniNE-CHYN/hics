import numpy
from PyQt5 import QtCore, QtWidgets, QtGui
from .mpl import MplCanvas
from .mplcolorcurve import ColorCurvesWindow
import matplotlib
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from .view import QHicsDataView

class NavigationToolbarImageCanvas(NavigationToolbar2QT):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        #('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        ('Colormap', 'Configure colormap', 'subplots', 'configure_cmap'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
        (None, None, None, None),
      )
    
    def configure_cmap(self):
        #Only possible if we have data...
        if self.parent.parent().hicsdataview is None:
            return
        dia = ColorCurvesWindow(self.parent, self.parent.parent().hicsdataview)
        dia.exec_()



class ImageCanvas(MplCanvas):
    _labels = {'x': 'x [px]', 'y': 'y [px]', 'l': '$\lambda$ [nm]'}
    def __init__(self, parent):
        super().__init__(parent)
        self.toolbar = NavigationToolbarImageCanvas(self, self)
        self._image = self.axes.imshow([[numpy.nan]], aspect='auto', interpolation = 'none')
        self._popmenu = QtWidgets.QMenu(self)
        
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        self.mpl_connect('motion_notify_event', self.__mpl_onmousemove)
        
        self._points = {}
        self._current_mouse_position = None
        
        self.__redraw_required = False
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self.__check_if_redraw_needed)
        timer.start(1000/25)
        
        
    def __mpl_onrelease(self, event):
        if event.button == 3:  #right click
            self._popmenu.clear()
            
            dpa = self.parent().data_point_available
            hdv = self.parent().hicsdataview
            
            if dpa is not None:
                action = self._popmenu.addAction("Add point")
                action.triggered.connect(lambda v: hdv.display_points_set(dpa, {hdv.spatial_axes[1]: event.xdata, hdv.spatial_axes[0]: event.ydata}))
            
            def _pdist_comp(p1, p2):
                acc = 0
                for k in p1.keys():
                    if k in p2.keys():
                        acc += (p1[k] - p2[k]) ** 2
                return numpy.sqrt(acc)
            
            pdists = [(k, _pdist_comp({hdv.spatial_axes[1]: event.xdata, hdv.spatial_axes[0]: event.ydata}, v)) for k, v in hdv.display_points.items() if v is not None]
            if len(pdists) > 0:
                nearest = pdists[numpy.argmin([x[1] for x in pdists])][0]
                action = self._popmenu.addAction("Remove nearest point")
                action.triggered.connect(lambda v: hdv.display_points_set(nearest, None))
                
            self._popmenu.addSeparator()
        
            action = self._popmenu.addAction("Export")
            action.triggered.connect(lambda v: self.parent().export())
            
            action = self._popmenu.addAction("Save as image")
            action.triggered.connect(lambda v: self.save_image())       
            
            self._popmenu.exec_(QtGui.QCursor().pos())
            
    def __mpl_onmousemove(self, event):
        try:
            self._current_mouse_position = (event.xdata, event.ydata)
        except:
            self._current_mouse_position = None
            
    def __check_if_redraw_needed(self):
        if self.__redraw_required:
            self.show_data()
            self.__redraw_required = False
            
    def redraw_required(self):
        self.__redraw_required = True
            
    def show_data(self):
        hdv = self.parent().hicsdataview
        if not hdv.valid:
            self._image.set_data([[numpy.nan]])
        else:
            data = hdv.data_to_display
            
            if data.ndim == 2:
                self._image.set_data(data)
                self._image.set_norm(hdv.cnorm_get(None))
                self._image.set_cmap(hdv.cm)
            else:
                data_norm = numpy.ma.zeros((data.shape[0], data.shape[1], numpy.clip(data.shape[2], 3, 4)))
                for band_id, band_color in enumerate('rgb'):
                    data_norm[:, :, band_id] = hdv.cnorm_get(hdv.display_bands[band_color])(data[:, :, band_id])
                #RGB images don't support masked values, so fill...
                #FIXME: (make empty pixels white?)
                self._image.set_data(data_norm.filled(0.))
            
            ax_y, ax_x = hdv.spatial_axes
        
            self.axes.set_xlabel(self._labels.get(ax_x, ax_x))
            self.axes.set_ylabel(self._labels.get(ax_y, ax_y))
        
            self._image.set_extent(hdv.get_ax_extent(ax_x) + hdv.get_ax_extent(ax_y)[::-1])
            self.axes.set_xlim(*hdv.get_ax_extent(ax_x))
            self.axes.set_ylim(*hdv.get_ax_extent(ax_y))
            
        self.draw()
        
    def show_points(self):
        hdv = self.parent()._hicsdataview
        for k, v in hdv.display_points.items():
            #FIXME: we could do a hline/vline when one of the dimensions is not defined
            if v is None or hdv.spatial_axes[1] not in v or hdv.spatial_axes[0] not in v:
                v = {hdv.spatial_axes[1]: numpy.nan, hdv.spatial_axes[0]: numpy.nan}
            if k not in self._points:
                self._points[k], = self.axes.plot([v[hdv.spatial_axes[1]]], [v[hdv.spatial_axes[0]]], '+', color=k)
            else:
                self._points[k].set_data([v[hdv.spatial_axes[1]]], [v[hdv.spatial_axes[0]]])
        
        self.draw()
        
    def save_image(self):
        fileName, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save image","","PNG files (*.png)")
        if fileName:
            self._image.write_png(fileName)
        
class DataCanvas(MplCanvas):
    _labels = {'x': 'x [px]', 'y': 'y [px]', 'l': '$\lambda$ [nm]'}
    def __init__(self, parent):
        super().__init__(parent)
        self._plots = {}
        self._current_mouse_position = None
        self._popmenu = QtWidgets.QMenu(self)
        
        self._vlines = {}
        
        self.mpl_connect('button_release_event', self.__mpl_onrelease)
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self._check_if_mouse_position_changed)
        timer.start(1000/25)
        

        
    def __mpl_onrelease(self, event):
        if event.button == 3:  #right click
            hdv = self.parent()._hicsdataview
            
            self._popmenu.clear()
            
            xidx = numpy.argmin(numpy.abs(event.xdata-hdv.data.get_ticks(hdv.data_axis)))
            
            action = self._popmenu.addAction("Set red")
            action.triggered.connect(lambda v: hdv.display_bands_set('r', xidx))
            
            action = self._popmenu.addAction("Set green")
            action.triggered.connect(lambda v: hdv.display_bands_set('g', xidx))
            
            action = self._popmenu.addAction("Set blue")
            action.triggered.connect(lambda v: hdv.display_bands_set('b', xidx))
            
            self._popmenu.addSeparator()
                
            action = self._popmenu.addAction("Clear red")
            action.triggered.connect(lambda v: hdv.display_bands_set('r', None))
        
            action = self._popmenu.addAction("Clear green")
            action.triggered.connect(lambda v: hdv.display_bands_set('g', None))
        
            action = self._popmenu.addAction("Clear blue")
            action.triggered.connect(lambda v: hdv.display_bands_set('b', None))
            
            self._popmenu.addSeparator()
            
            action = self._popmenu.addAction("Export")
            action.triggered.connect(lambda v: self.parent().export())
            

            
            self._popmenu.exec_(QtGui.QCursor().pos())
            
            
                
        
    def _check_if_mouse_position_changed(self):
        im_position = self.parent()._canvas_image._current_mouse_position
        if im_position != self._current_mouse_position:
            self._current_mouse_position = im_position
            self.show_data(True)
        
    def show_data(self, only_current=False):
        hdv = self.parent()._hicsdataview
        if not hdv.valid:
            return
        
        xaxis = hdv.data_axis
        if self._current_mouse_position is None or self._current_mouse_position[0] is None or self._current_mouse_position[1] is None:
            items = [(None, None)]
        else:
            items = [(None, {hdv.spatial_axes[1]: self._current_mouse_position[0], hdv.spatial_axes[0]: self._current_mouse_position[1]})]
        
        if not only_current:
            items += list(hdv.display_points.items())
            
        xdata = hdv.data.get_ticks(xaxis)
        for k, pos in items:
            if pos is not None:
                ydata = hdv.data.data_at(pos, [xaxis])
                vdata = numpy.sqrt(hdv.data.var_at(pos, [xaxis]))
                
                xdata = numpy.array(xdata)
                ydata = numpy.array(ydata)
                ydataP = ydata + vdata
                ydataM = ydata - vdata
    
                if k not in self._plots:
                    if k is None:
                        zorder = 10
                        color = 'k'
                    else:
                        zorder = 0
                        color = k
                    
                    self._plots[k] = [
                        self.axes.plot(xdata, ydata, color=color, zorder=zorder)[0],
                        self.axes.plot(xdata, ydataP, '--', color=color, zorder=zorder)[0],
                        self.axes.plot(xdata, ydataM, '--', color=color, zorder=zorder)[0]
                    ]
                else:
                    self._plots[k][0].set_data(xdata, ydata)
                    self._plots[k][1].set_data(xdata, ydataP)
                    self._plots[k][2].set_data(xdata, ydataM)
            else:
                if k in self._plots:
                    #Hide plot if it exists
                    self._plots[k][0].set_data([numpy.nan], [numpy.nan])
                    self._plots[k][1].set_data([numpy.nan], [numpy.nan])
                    self._plots[k][2].set_data([numpy.nan], [numpy.nan])                    
                
        for color, band_id in hdv.display_bands.items():
            
            if color in self._vlines:
                self.axes.lines.remove(self._vlines[color])
                del self._vlines[color]
            if band_id is None:
                continue
            
            band_wavelength = xdata[band_id]
            self._vlines[color] = self.axes.axvline(band_wavelength, color=color)
            
                
        self.axes.relim()
        if self.axes.dataLim.x0 != self.axes.dataLim.x1 and numpy.isfinite(self.axes.dataLim.x0) and numpy.isfinite(self.axes.dataLim.x1):
            self.axes.set_xlim(self.axes.dataLim.x0, self.axes.dataLim.x1)
        if self.axes.dataLim.y0 != self.axes.dataLim.y1 and numpy.isfinite(self.axes.dataLim.y0) and numpy.isfinite(self.axes.dataLim.y1):
            self.axes.set_ylim(self.axes.dataLim.y0, self.axes.dataLim.y1)
        self.draw()
        
class HicsDataViewWidget(QtWidgets.QSplitter):
    
    def __init__(self, parent=None):
        super().__init__(QtCore.Qt.Vertical, parent)
        
        self._data_points = dict([(x, None) for x in  matplotlib.rcParams['axes.prop_cycle'].by_key()['color']])
        
        self._canvas_image = ImageCanvas(self)
        self._canvas_data = DataCanvas(self)
        
        self.insertWidget(0, self._canvas_image)
        self.insertWidget(1, self._canvas_data)
        
        self._hicsdataview = QHicsDataView()
        
        self._hicsdataview.display2dChanged.connect(self._canvas_image.redraw_required)
        #Thisis cheap to do...
        self._hicsdataview.display2dChanged.connect(self._canvas_data.show_data)
        self._hicsdataview.display1dChanged.connect(self._canvas_data.show_data)
        self._hicsdataview.displayPointsChanged.connect(self._canvas_image.show_points)
        self._hicsdataview.displayPointsChanged.connect(self._canvas_data.show_data)
        
    @property
    def data_point_available(self):
        dp = self._hicsdataview.display_points
        for k in sorted(dp.keys()):
            if dp[k] is None:
                return k
        return None
        
    @property
    def hicsdataview(self):
        return self._hicsdataview
    
    def export(self):
        pass
