import numpy
from PyQt5 import QtCore, QtWidgets
from .mpl import MplCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT

class NavigationToolbarImageCanvas(NavigationToolbar2QT):
    toolitems = (
        ('Home', 'Reset original view', 'home', 'home'),
        ('Back', 'Back to  previous view', 'back', 'back'),
        ('Forward', 'Forward to next view', 'forward', 'forward'),
        (None, None, None, None),
        ('Pan', 'Pan axes with left mouse, zoom with right', 'move', 'pan'),
        ('Zoom', 'Zoom to rectangle', 'zoom_to_rect', 'zoom'),
        ('Subplots', 'Configure subplots', 'subplots', 'configure_subplots'),
        (None, None, None, None),
        ('Save', 'Save the figure', 'filesave', 'save_figure'),
      )
    
    def configure_subplots(self):
        image = os.path.join(matplotlib.rcParams['datapath'], 'images', 'matplotlib.png')
        dia = SubplotToolQt(self.canvas.figure, self.parent)
        dia.setWindowIcon(QtGui.QIcon(image))
        dia.exec_()


class ImageCanvas(MplCanvas):
    _labels = {'x': 'x [px]', 'y': 'y [px]', 'l': '$\lambda$ [nm]'}
    def __init__(self, parent):
        super().__init__(parent)
        self.toolbar = NavigationToolbarImageCanvas(self, self)
        self._image = self.axes.imshow([[numpy.nan]], aspect='auto', interpolation = 'none')
        
    def show_data(self):
        if self.parent().hicsdataview is None:
            self._image.set_data([[numpy.nan]])
        else:
            hdv = self.parent().hicsdataview
            data = hdv.data_to_display
            
            if data.ndim == 2:
                self._image.set_data(data)
                self._image.set_norm(hdv.get_norm(0))
                self._image.set_cmap('gray')
            else:
                #FIXME
                data_norm = numpy.ma.zeros((data.shape[0], data.shape[1], numpy.clip(data.shape[2], 3, 4)))
                for d in range(data.shape[2]):
                    data_norm[:, :, d] = hdv.get_norm(d)(data[:, :, d])
                self._image.set_data(data)
            
            ax0, ax1 = hdv.data_to_display_axes
        
            self.axes.set_xlabel(self._labels.get(ax1, ax1))
            self.axes.set_ylabel(self._labels.get(ax0, ax0))
        
            self._image.set_extent(hdv.get_ax_extent(ax1) + hdv.get_ax_extent(ax0)[::-1])            
            
        self.draw()
        
class HicsDataViewWidget(QtWidgets.QSplitter):
    dataChanged = QtCore.pyqtSignal(name='dataChanged')
    def __init__(self, parent=None):
        super().__init__(QtCore.Qt.Vertical, parent)
        self._canvas_image = ImageCanvas(self)
        
        self.insertWidget(0, self._canvas_image)
        self._hicsdataview = None
        
        self.dataChanged.connect(self._canvas_image.show_data)
        
    @property
    def hicsdataview(self):
        return self._hicsdataview
    
    @hicsdataview.setter
    def hicsdataview(self, newvalue):
        #FIXME: connect signals
        self._hicsdataview = newvalue
        self.dataChanged.emit()


#class MyMplCanvas(FigureCanvas):
    #"""Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""
    #_default_name = 'Canvas'
    #newMouseMoveEvent = QtCore.pyqtSignal(name='newMouseMoveEvent')
    
    #def __init__(self, parent=None):
        #fig = Figure(figsize=(5, 4), dpi=100)
        #self.axes = fig.add_subplot(111)
        ## We want the axes cleared every time plot() is called
        ##self.axes.hold(False)

        #FigureCanvas.__init__(self, fig)
        #self.setParent(parent)
        #self.toolbar = NavigationToolbar(self, self)
        
        #self.mpl_connect('motion_notify_event', self.__mpl_motion_notify_event)
        #self.mpl_connect('button_press_event', self.__mpl_motion_notify_event)
        
        #self._name = None
        #self._mpl_mousemove_event_queue = queue.PriorityQueue()
        
        #self.__mpl_motion_notify_event_process_timer = QtCore.QTimer(self)
        #self.__mpl_motion_notify_event_process_timer.timeout.connect(self.__mpl_motion_notify_event_process)
        #self.__mpl_motion_notify_event_process_timer.start(100)
        
    #def _get_data_for(self, x, y):
        #return None

    #@property
    #def name(self):
        #if self._name is None:
            #return self._default_name
        #else:
            #return self._name
        
    #@name.setter
    #def name(self, newvalue):
        #self._name = newvalue

        
    #def resizeEvent(self, event):
        #FigureCanvas.resizeEvent(self, event)
        
        #try:
            #tb_width, tb_height = self.figure.transFigure.inverted().transform((0, self.toolbar.height()))
        #except numpy.linalg.linalg.LinAlgError:
            ##If singular, then abort
            #return
        
        #try:
            #self.figure.tight_layout(rect=(0, 0, 1, 1-tb_height))
        #except ValueError:
            ##Ignore ValueErrors where rect is invalid
            #pass
        
    #def __mpl_motion_notify_event(self, event):
        ##Handling event can be slow, so we put it in a queue
        ##Lower is higher priority
        #priority = {True: 0, False: 10}[event.button is not None]
        #self._mpl_mousemove_event_queue.put((priority, -time.time(), event))
        #self.newMouseMoveEvent.emit()
        
        
    #def __mpl_motion_notify_event_process(self):
        #try:
            #priority, mtime, event = self._mpl_mousemove_event_queue.get(block = False)
        #except queue.Empty:
            #return
        
        
        ##Flush queue
        #while not self._mpl_mousemove_event_queue.empty():
            #self._mpl_mousemove_event_queue.get()
        
        #if event.inaxes != self.axes:
            #self._mouse_move(None, None, None, event)
            #return

        #x = float(event.xdata)
        #y = float(event.ydata)
        #data = None
        
        #if event.inaxes and event.inaxes.get_navigate():
            #data = self._get_data_for(x, y)
        
        #self._mouse_move(x, y, data, event)
        
    #def leaveEvent(self, event):
        #self._mouse_move(None, None, None, False)
        #super().leaveEvent(event)
        
    #def _mouse_move(self, x, y, data, event):
        #pass
        
#class FrameCanvas(MyMplCanvas):
    #_default_name = 'Frame'
    
    #def __init__(self, parent=None):
        #super().__init__(parent)
        #self.axes.set_xlim(self.window().wavelengths.min(), self.window().wavelengths.max())
        #self.axes.set_xlabel('Wavelength [nm]')
        #self.axes.set_ylabel('y [px]')
        #self._image = None
        #self._data = None
        
    #def _get_data_for(self, x, y):
        #if x is None or y is None or self._data is None:
            #return None
        #if y > self._data.shape[0] or x > self._data.shape[1]:
            #return None
        
        #return self._data[y, x]
        
        
    #def imshow(self, data):
        #if data.ndim == 3 and data.shape[1] == 1:
            #data = data[:, 0, :]
            
        #self._data = data
            
        #if self._image is None:
            #self._image = self.axes.imshow(data, aspect='auto', interpolation = 'none')
        #else:
            #self._image.set_data(data)

        #self._image.set_extent([self.window().wavelengths.min(), self.window().wavelengths.max(), 0, data.shape[0]])

        #if hasattr(data, 'compressed'):
            #self._image.set_clim(numpy.percentile(data.compressed(), 1), numpy.percentile(data.compressed(), 99))
        #else:
            #self._image.set_clim(numpy.percentile(data.flatten(), 1), numpy.percentile(data.flatten(), 99))
        #self.draw()
        
    #def _mouse_move(self, x, y, data, event):
        #if x is not None and y is not None:
            #wavelengths = self.window().wavelengths
            #best_wl = wavelengths[numpy.abs(wavelengths-x).argmin()]
            
            #s = '{}: λ={:.02f}nm, y={}px [{}]'.format(self.name, best_wl, int(numpy.round(y, 0)), data)
        #else:
            #s = None
            
        #self.window().statusbar_update(s)
        
#class ImageCanvas(MyMplCanvas):
    #_default_name = 'Image'
    #_perc_min = 1
    #_perc_max = 99
    
    #def __init__(self, parent=None):
        #super().__init__(parent)
        #self.axes.set_xlabel('x [px]')
        #self.axes.set_ylabel('y [px]')
        #self.window().colorCoordinatesChanged.connect(self.refresh_plot)
        
        #self._name = None
        #self._image = None
        #self._data = None
        #self._markers = {}
        #self._wavelengths_ids = []
        
    #def imshow(self, data):
        #self._data = data
        #self.refresh_plot(force=True)
        
    #def _get_data_for(self, x, y):
        #if x is None or y is None or self._data is None:
            #return None
        #x = int(x)
        #y = int(y)
        #if y > self._data.shape[0] or x > self._data.shape[1]:
            #return None
        
        #wl_ids = [x for x in self._wavelengths_ids if x is not None]
        
        #if len(wl_ids) == 0:
            #return numpy.ma.average(numpy.ma.masked_invalid(self._data[y, x]))
        #elif len(wl_ids) == 1:
            #return self._data[y, x, wl_ids[0]]
        #else:
            #r = []
            #for wl_id in self._wavelengths_ids:
                #if wl_id is not None:
                    #r.append(self._data[y, x, wl_id])
                #else:
                    #r.append(None)
            #return r
        
    #def refresh_plot(self, force=False):
        #if self._data.ndim == 3:
            #new_wavelengths_ids = [self.window()._color_coordinates.get(c, (None, None))[0] for c in ('sr', 'sg', 'sb')]
        #else:
            #new_wavelengths_ids = [self.window()._color_coordinates.get(c, (None, None))[0] for c in ('c')]
            
        
        #if new_wavelengths_ids != self._wavelengths_ids or force:
            #selected_wavelengths_ids = [x for x in new_wavelengths_ids if x is not None]
            #if self._data.ndim == 4:
                
                #if len(selected_wavelengths_ids) > 0:
                    #endmember_id = selected_wavelengths_ids[0]
                #else:
                    #endmember_id = 0
                ##Classification
                #k = '{}-cache-{}-avg'.format(self.name, endmember_id)
                #if k not in self.window()._m:
                    #data = numpy.ma.average(numpy.ma.masked_invalid(self._data[:, :, endmember_id, :]), 2).filled(numpy.nan)
                    #if self.window()._m.writable:
                        #self.window()._m[k] = data
                #else:
                    #data = self.window()._m[k]
                #self._im_cache = data
            #else:
                #if len(selected_wavelengths_ids) == 0:
                    #self._im_cache = numpy.ma.average(numpy.ma.masked_invalid(self._data), 2)
                #elif len(selected_wavelengths_ids) == 1:
                    #wl = selected_wavelengths_ids[0]
                    #self._im_cache = self._data[:, :, wl]
                #else:
                    #self._im_cache = numpy.ma.zeros(self._data.shape[:2]+(3, ))
                    #for im_cache_idx, wl in enumerate(new_wavelengths_ids):
                        #if wl is not None:
                            #wl_data = numpy.ma.masked_invalid(self._data[:, :, wl])
                            #if hasattr(wl_data, 'compressed'):
                                #wl_data_min = numpy.percentile(wl_data.compressed(), self._perc_min)
                                #wl_data_max = numpy.percentile(wl_data.compressed(), self._perc_max)
                            #else:
                                #wl_data_min = numpy.percentile(wl_data.flatten(), self._perc_min)
                                #wl_data_max = numpy.percentile(wl_data.flatten(), self._perc_max)
                            #print(wl, wl_data_min, wl_data_max)
                            #wl_data = numpy.clip((wl_data - wl_data_min) / (wl_data_max - wl_data_min), 0, 1)
                            #self._im_cache[:, :, im_cache_idx] = wl_data
                    
        #self._wavelengths_ids = new_wavelengths_ids
                
        #if self._image is None:
            #self._image = self.axes.imshow(self._im_cache, aspect='auto', interpolation = 'none')
            #self.axes.set_xlim([0, self._data.shape[1]])
            #self.axes.set_ylim([self._data.shape[0], 0])            
        #else:
            #self._image.set_data(self._im_cache)

        #self._image.set_extent([0,self._data.shape[1], self._data.shape[0], 0])

        #if hasattr(self._im_cache, 'compressed'):
            #self._image.set_clim(numpy.percentile(self._im_cache.compressed(), self._perc_min), numpy.percentile(self._im_cache.compressed(), self._perc_max))
        #else:
            #cdata = numpy.ma.masked_invalid(self._im_cache).compressed()
            #if cdata.shape[0] > 0:
                #self._image.set_clim(numpy.percentile(cdata, self._perc_min), numpy.percentile(cdata, self._perc_max))
        
        #self._refresh_spectrum_plots()
        #self.draw()
        
    #def _refresh_spectrum_plots(self):
        #color_visible = []
        #for k, coordinates in self.window()._color_coordinates.items():
            #if not k.startswith('i'):
                #continue
            #color = k[1:]
            #x, y = coordinates
            
            #color_visible.append(color)
            
            #self._spectrum_plot_do(x, y, color)
            
            #if color not in self._markers:
                #marker, = self.axes.plot([0], [0], color+'+', markersize=10, markeredgewidth=1, visible=False)
                #self._markers[color] = marker
                
            #self._markers[color].set_data([x], [y])
            #self._markers[color].set_visible(True)
            
        #for color in self._markers:
            #if color not in color_visible:
                #self._markers[color].set_visible(False)
                #self._spectrum_plot_do(None, None, color)
        
    #def _spectrum_plot_do(self, x, y, color):
        #if self._data.ndim == 3:
            #if self._data is not None and x is not None and y is not None and y < self._data.shape[0] and x < self._data.shape[1]:
                #spectrum = self._data[y, x]
                #variance = None
                #if self.name + '-var' in self.window()._m:
                    #variance = self.window()._m[self.name + '-var'][y, x]
                #self.window()._canvas_spectrum.set_data(spectrum, color, variance=variance)
            #else:
                #self.window()._canvas_spectrum.set_data(None, color)
        #elif self._data.ndim == 4:
            #if self._data is not None and x is not None and y is not None and y < self._data.shape[0] and x < self._data.shape[1]:
                #classification_data = self._data[y, x]
                #self.window()._canvas_classification.set_data(classification_data)
            #else:
                #self.window()._canvas_classification.set_data(None)
        
    #def _mouse_move(self, x, y, data, event):
        #if x is not None and y is not None:
            #x, y = int(x), int(y)
            
            #if event.button == 1 and self.window()._color_action_waiting is not None and self.window()._color_action_waiting.startswith('i'):
                #self.window()._color_set_coordinates(x, y)
                #self.draw()
            
            #s = '{}: x={}px, y={}px [{}]'.format(self.name, x, y, data)
            #self._spectrum_plot_do(x, y, 'k')
            
        #else:
            #s = None
            #self.window()._canvas_spectrum.set_data(None, 'k')
            
        #self.window().statusbar_update(s)
        
        

#class SpectrumCanvas(MyMplCanvas):
    #_default_name = 'Spectrum'
    
    #def __init__(self, parent=None):
        #super().__init__(parent)
        #self.axes.set_xlim(self.window().wavelengths.min(), self.window().wavelengths.max())
        #self.axes.set_xlabel('Wavelength [nm]')
        #self.axes.set_ylabel('')
        
        #self._plots = {}
        #self._vlines = {}
        
        #self.window().colorCoordinatesChanged.connect(self.refresh_plot)
        
    #def refresh_plot(self):
        #wavelengths = self.window().wavelengths
        #for c in ('sr', 'sg', 'sb'):
            #color = c[1:]
            #if c not in self.window()._color_coordinates:
                #if color in self._vlines:
                    #del self._vlines[color]
                #continue
            #wl_id = self.window()._color_coordinates[c][0]
            
            #self._vlines[color] = self.axes.axvline(wavelengths[wl_id], color=color)
        
        #all_plots = sum(self._plots.values(), []) + list(self._vlines.values())
        
        #for i, l in reversed(list(enumerate(self.axes.lines))):
            #if l not in all_plots:
                #self.axes.lines.pop(i)
            
        #self.axes.relim()
        #self.axes.set_ylim(0, self.axes.dataLim.y1)
            
        #self.draw()
        
    #def set_data_only(self, data, color, variance=None):
        #self._plots = {}
        #return self.set_data(data, color, variance)
        
    #def set_data(self, data, color, variance=None):
        #if color not in self._plots:
            #self._plots[color] = [None, None, None]  #median, min_dash, max_dash
            
        
        #if data is not None:
            #if self._plots[color][0] is None:
                #self._plots[color][0] = self.axes.plot(self.window().wavelengths, data, color)[0]
            #self._plots[color][0].set_data((self.window().wavelengths, data))
            
            #if variance is not None:
                #if self._plots[color][1] is None:
                    #self._plots[color][1] = self.axes.plot(self.window().wavelengths, data, color+'--')[0]
                    #self._plots[color][2] = self.axes.plot(self.window().wavelengths, data, color+'--')[0]
                    
                #self._plots[color][1].set_data((self.window().wavelengths, data+numpy.sqrt(variance)))
                #self._plots[color][2].set_data((self.window().wavelengths, data-numpy.sqrt(variance)))
            #else:
                #self._plots[color][1] = None
                #self._plots[color][2] = None
        #else:
            #del self._plots[color]
            
        #self.refresh_plot()
        
    #def _mouse_move(self, x, y, data, event):
        #if x is not None and y is not None:
            #wavelengths = self.window().wavelengths
            #wavelength_id = numpy.abs(wavelengths-x).argmin()
            #best_wl = wavelengths[wavelength_id]
            
            
            #if event.button == 1 and self.window()._color_action_waiting is not None and self.window()._color_action_waiting.startswith('s'):
                #self.window()._color_set_coordinates(wavelength_id, None)
                #self.draw()

            
            #s = '{}: λ={:.02f}nm, y={} [{}]'.format(self.name, best_wl, y, data)
        #else:
            #s = None
            
        #self.window().statusbar_update(s)
        
        
#class ClassificationCanvas(MyMplCanvas):
    #_default_name = 'Classification'
    
    #def __init__(self, parent=None):
        #super().__init__(parent)
        #self.axes.set_xlabel('')
        #self.axes.set_ylabel('Abundance [-]')
        
        #if 'endmembers' in self.window()._m:
            #endmembers = self.window()._m['endmembers']
            #library = self.window()._m['library']
            #self.axes.set_xticks(list(range(len(endmembers))))
            #self.axes.set_xticklabels([library[x+'-label'] for x in endmembers], rotation='vertical')
            
            #self.axes.set_xlim(-0.5, len(endmembers) - 0.5)
            #self.axes.set_ylim(0, 1)
            
            #try:
                ##Only valid for recent versions of matplotlib
                #from cycler import cycler
                #self.axes.set_prop_cycle(cycler('color', ['k']))
            #except ImportError:
                #pass
            
            #self._plots = None
            #self.window().colorCoordinatesChanged.connect(self.refresh_plot)
            
    #def refresh_plot(self):
        #self.draw()
        
    #def set_data(self, data):
        #if self._plots is not None:
            #for k in self._plots.keys():
                #if type(self._plots[k]) == list:
                    #for a in self._plots[k]:
                        #a.remove()
                #else:
                    #self._plots[k].remove()
                    
            #self._plots = None
            
        #if data is not None:
            #if data.shape[1] == 1:
                #r = self.axes.bar(numpy.arange(0, data.shape[0]), data[:, 0])
                #self._plots = {'bars': r}
            #else:
                #vpos = numpy.nonzero(numpy.ma.masked_invalid(data).var(1))[0]
                #violindata = [numpy.ma.masked_invalid(x).compressed() for x in data[vpos]]
                #if len(vpos) > 0:
                    #self._plots = self.axes.violinplot(violindata,vpos,showmedians=True)
                ##self._plots = self.axes.violinplot(data[vpos].T),vpos,showmedians=True)
                
        #self.refresh_plot()
        
    #def _mouse_move(self, x, y, data, event):
        #if x is not None and y is not None:
            #endmember_id = int(round(x, 0))
            
            #if event.button == 1:
                #self.window()._color_set_coordinates(endmember_id, None, 'c')
                #self.draw()

            #endmembers = self.window()._m['endmembers']
            #library = self.window()._m['library']            
            #s = 'Endmember: {}'.format(library[endmembers[endmember_id]+'-description'])
        #else:
            #s = None
            
        #self.window().statusbar_update(s)
        
    


#class ApplicationWindow(QtWidgets.QMainWindow):
    #colorCoordinatesChanged = QtCore.pyqtSignal(name='colorCoordinatesChanged')
    #dictKeysChanged = QtCore.pyqtSignal(name='dictKeysChanged')
    #keyChanged = QtCore.pyqtSignal(name='keyChanged')
    
    #mouseMove = QtCore.pyqtSignal(object, float, float, float, bool, name='mouseMove')
    
    #def __init__(self, f):
        #QtWidgets.QMainWindow.__init__(self)
        #self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        #self.setWindowTitle("Data file viewer")
        
        #if f.startswith('http://') or f.startswith('https://'):
            #self._m = httpdict(f)
        #else:
            #if not os.path.exists(f):
                #raise ValueError('File {} does not exist!'.format(f()))
            ##self._m = mmapdict(f, not os.access(f, os.W_OK))
            #self._m = mmapdict(f, True)
        
        #self._data_list = QtWidgets.QListWidget(self)
        #self._data_list.currentTextChanged.connect(self._key_changed)
        
        #self._canvas_image = ImageCanvas(self)
        #self._canvas_frame = FrameCanvas(self)
        #self._canvas_spectrum = SpectrumCanvas(self)
        #self._canvas_classification = ClassificationCanvas(self)
        #self._description_area = QtWidgets.QTextBrowser()
        ##self._figure_image.toolbar.buttons
        
        #self.toolbar = self.addToolBar('Toolbar')
        
        #self._color_actions = {}
        #self._color_coordinates = {}
        #for color in ('ir', 'ig', 'ib', 'sr', 'sg', 'sb'):
            #action = QtWidgets.QAction(color, self)
            #action.setCheckable(True)
            #action.triggered.connect(functools.partial(self._color_action_triggered, color))
            #self.toolbar.addAction(action)
            #self._color_actions[color] = action
        
        #self._splitter_plots = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        #self._splitter_plots.insertWidget(0, self._canvas_image)
        #self._splitter_plots.insertWidget(1, self._canvas_frame)
        #self._splitter_plots.insertWidget(2, self._canvas_spectrum)
        #self._splitter_plots.insertWidget(3, self._canvas_classification)
        #self._splitter_plots.insertWidget(4, self._canvas_classification)
        #self._splitter_plots.insertWidget(5, self._description_area)
        
        #self._canvas_spectrum.hide()
        
        #self._splitter_data = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        #self._splitter_data.insertWidget(0, self._data_list)
        #self._splitter_data.insertWidget(1, self._splitter_plots)
        #self.setCentralWidget(self._splitter_data)
        
        #self.file_menu = QtWidgets.QMenu('&File', self)
        #self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        #self.menuBar().addMenu(self.file_menu)
        
        #self._current_key = None
        #self.keyChanged.connect(self._key_changed)
        
        #self._m_old_commit_number = None
        #self.dictKeysChanged.connect(self._mmapdict_changed)
        #self.dictKeysChanged.emit()
        
        #timer = QtCore.QTimer(self)
        #timer.timeout.connect(self._check_if_mmapdict_changed)
        #timer.start(1000)

        ##self.main_widget = QtWidgets.QWidget(self)

        ##l = QtWidgets.QVBoxLayout(self.main_widget)
        ##self.mdiwidget = QtWidgets.QMdiArea()
        ##l.addWidget(self.mdiwidget)
        
        ##self.main_widget.setFocus()
        ##self.setCentralWidget(self.main_widget)
        
    #def _check_if_mmapdict_changed(self):
        #if self._m_old_commit_number != self._m.commit_number:
            #self.dictKeysChanged.emit()
        
    #def _mmapdict_changed(self):
        #self._m_old_commit_number = self._m.commit_number
        
        #self._data_list.blockSignals(True)
        
        #self._data_list.clear()
        #for k in sorted(self._m.keys()):
            #self._data_list.addItem(k)
        
        #found = False
        #for i in range(self._data_list.count()):
            #item = self._data_list.item(i)
            #if item.text() == self._current_key:
                #item.setSelected(True)
                #found = True
                
        #if not found:
            #self._key_changed(None)
            
        #self._data_list.blockSignals(False)
        #self.statusbar_update()
        
        

        
    #def statusbar_update(self, message=None):
        #if message is None:
            #description = self._m['description']
            #description_lines = description.split('\n')
            #self.statusBar().showMessage(description_lines[0])
            #if len(description_lines) > 1:
                #self.statusBar().setToolTip(description)
            #else:
                #self.statusBar().setToolTip(None)
        #else:
            #self.statusBar().showMessage(message)
            
    #@property
    #def wavelengths(self):
        #return numpy.array(self._m['wavelengths'])
        
    #def _key_changed(self, new_key):
        #self._current_key = new_key
        
        #sizes_before = self._splitter_plots.sizes()

        #canvas_image_visible = False    
        #canvas_frame_visible = False
        #canvas_spectrum_visible = False
        #canvas_classification_visible = False
        #description_area_visible = False
        
        #if new_key is None:
            #description_area_visible = True
            #self._description_area.setText(self._m['description'])
        #elif isinstance(self._m[new_key], numpy.ndarray):
            #data = self._m[new_key]
            
            #if data.ndim == 1:
                #if new_key + '-var' in self._m:
                    #self._canvas_spectrum.set_data_only(data, 'k', variance=self._m[new_key+'-var'])
                #else:
                    #self._canvas_spectrum.set_data_only(data, 'k')
                    
                #canvas_spectrum_visible = True
                
            #elif data.ndim == 2 or (data.ndim == 3 and data.shape[1] == 1):
                #self._canvas_frame.name = new_key
                #self._canvas_frame.imshow(data)
                
                #canvas_frame_visible = True
            #elif data.ndim == 3:
                #self._canvas_image.name = new_key
                #self._canvas_image.imshow(data)
                
                #canvas_image_visible = True
                #canvas_spectrum_visible = True
            #elif data.ndim == 4:
                #self._canvas_image.name = new_key
                #self._canvas_image.imshow(data)
            
                #canvas_image_visible = True
                #canvas_classification_visible = True                
            
        #else:
            #description_area_visible = True
            #data = self._m[new_key]
            #if type(data) == str:
                #self._description_area.setText(data)
            #else:
                #self._description_area.setText(pprint.pformat(data, width=1000))            
        
        
        #if canvas_image_visible:
            #self._canvas_image.show()
            ##self._canvas_image.draw()
        #else:
            #self._canvas_image.hide()
            
        #if canvas_frame_visible:
            #self._canvas_frame.show()
            #self._canvas_frame.draw()
        #else:
            #self._canvas_frame.hide()
            
        #if canvas_spectrum_visible:
            #self._canvas_spectrum.show()
            #self._canvas_spectrum.draw()
        #else:
            #self._canvas_spectrum.hide()
            
        #if canvas_classification_visible:
            #self._canvas_classification.show()
            #self._canvas_classification.draw()
        #else:
            #self._canvas_classification.hide()
            
        #if description_area_visible or (not canvas_image_visible and not canvas_frame_visible and not canvas_spectrum_visible and not canvas_classification_visible):
            #self._description_area.show()
        #else:
            #self._description_area.hide()
            
        
    #def _color_action_triggered(self, color):
        #if self._color_actions[color].isChecked():
            ##Only one color can be checked without coordinates at the same time
            #for c in self._color_actions:
                #if c not in self._color_coordinates and c != color:
                    #self._color_actions[c].setChecked(False)
        #else:
            #if color in self._color_coordinates:
                #del self._color_coordinates[color]
                #self.colorCoordinatesChanged.emit()
            
    #@property
    #def _color_action_waiting(self):
        #for c in self._color_actions:
            #if self._color_actions[c].isChecked() and c not in self._color_coordinates:
                #return c
        #return None
    
    
    #def _color_set_coordinates(self, x, y, color=None):
        #if color is None:
            #color = self._color_action_waiting
        #assert color is not None
        
        #self._color_coordinates[color] = (x, y)
        #self.colorCoordinatesChanged.emit()
        
    #def fileQuit(self):
        #self.close()

    #def closeEvent(self, ce):
        #self.fileQuit()

#if __name__ == '__main__':
    #import sys
    #qApp = QtWidgets.QApplication(sys.argv)
    
    #aw = ApplicationWindow(sys.argv[1])
    #aw.show()
    #sys.exit(qApp.exec_())


