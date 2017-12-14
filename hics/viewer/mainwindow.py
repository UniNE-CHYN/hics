
from PyQt5 import QtCore, QtWidgets

from mmappickle import mmapdict, httpdict

import numpy
import pprint

import re
import queue
import functools
import time
import os

import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from hics.viewer.viewwidget import HicsDataViewWidget
from hics.viewer.view import HicsDataView, HicsData


class ApplicationWindow(QtWidgets.QMainWindow):
    colorCoordinatesChanged = QtCore.pyqtSignal(name='colorCoordinatesChanged')
    dictKeysChanged = QtCore.pyqtSignal(name='dictKeysChanged')
    keyChanged = QtCore.pyqtSignal(name='keyChanged')
    
    mouseMove = QtCore.pyqtSignal(object, float, float, float, bool, name='mouseMove')
    
    def __init__(self, f):
        QtWidgets.QMainWindow.__init__(self)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.setWindowTitle("Data file viewer")
        
        self._f = f
        if f.startswith('http://') or f.startswith('https://'):
            self._m = httpdict(f)
        else:
            if not os.path.exists(f):
                raise ValueError('File {} does not exist!'.format(f))
            #self._m = mmapdict(f, not os.access(f, os.W_OK))
            self._m = mmapdict(f, True)
        
        self._data_list = QtWidgets.QListWidget(self)
        self._data_list.currentTextChanged.connect(self._key_changed)
        
        self._view_widget = HicsDataViewWidget(self)
        
        self._text_widget = QtWidgets.QTextEdit(self)
        self._text_widget.setReadOnly(True)
        self._text_widget.hide()
        
        self._splitter_data = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._splitter_data.insertWidget(0, self._data_list)
        self._splitter_data.insertWidget(1, self._view_widget)
        self._splitter_data.insertWidget(2, self._text_widget)
        self.setCentralWidget(self._splitter_data)
        
        self.file_menu = QtWidgets.QMenu('&File', self)
        self.file_menu.addAction('&Quit', self.fileQuit, QtCore.Qt.CTRL + QtCore.Qt.Key_Q)
        self.menuBar().addMenu(self.file_menu)
        
        self._current_key = None
        self.keyChanged.connect(self._key_changed)
        
        self._m_old_commit_number = None
        self.dictKeysChanged.connect(self._mmapdict_changed)
        self.dictKeysChanged.emit()
        
        timer = QtCore.QTimer(self)
        timer.timeout.connect(self._check_if_mmapdict_changed)
        timer.start(1000)

        #self.main_widget = QtWidgets.QWidget(self)

        #l = QtWidgets.QVBoxLayout(self.main_widget)
        #self.mdiwidget = QtWidgets.QMdiArea()
        #l.addWidget(self.mdiwidget)
        
        #self.main_widget.setFocus()
        #self.setCentralWidget(self.main_widget)
        
    def _check_if_mmapdict_changed(self):
        if self._m_old_commit_number != self._m.commit_number:
            self.dictKeysChanged.emit()
        
    def _mmapdict_changed(self):
        self._m_old_commit_number = self._m.commit_number
        
        self._data_list.blockSignals(True)
        
        self._data_list.clear()
        for k in sorted(self._m.keys()):
            self._data_list.addItem(k)
        
        found = False
        for i in range(self._data_list.count()):
            item = self._data_list.item(i)
            if item.text() == self._current_key:
                item.setSelected(True)
                found = True
                
        if not found:
            self._key_changed(None)
            
        self._data_list.blockSignals(False)
        self.statusbar_update()
        
        

        
    def statusbar_update(self, message=None):
        if message is None:
            description = self._m['description']
            description_lines = description.split('\n')
            self.statusBar().showMessage(description_lines[0])
            if len(description_lines) > 1:
                self.statusBar().setToolTip(description)
            else:
                self.statusBar().setToolTip(None)
        else:
            self.statusBar().showMessage(message)
            
    @property
    def wavelengths(self):
        return numpy.array(self._m['wavelengths'])
        
    def _key_changed(self, new_key):
        import re
        self._current_key = new_key
        
        if self._current_key not in self._m:
            return
        
        data = self._m[self._current_key]
        hdv = self._view_widget.hicsdataview
        
        if re.match('^refl-[0-9]{5}-w$', new_key):
            dims = ('y', 'l')
        elif hasattr(data, 'shape'):
            if data.ndim == 3:
                dims = ('y', 'x', 'l')
                hdv.spatial_axes = ['y', 'x']
                if data.shape[1] == 1:
                    hdv.spatial_axes = ['y', 'l']
            else:
                print(data.shape)
                return
        else:
            self._text_widget.setText(self._to_html(self._current_key))
            
            self._text_widget.show()
            self._view_widget.hide()
            
            return
        
        self._text_widget.hide()
        self._view_widget.show()        
        self._view_widget.hicsdataview.data = HicsData(self._f, self._current_key, dims, 'DN')
        
    def _to_html(self, key):
        data = self._m[key]
        if type(data) == str:
            return data
        elif type(data) == dict and re.match('^(scan|white)-[0-9]+-p$', key):
            #Scan properties
            r = ['<table border=1 width="100%">']
            klist = list(data.keys())
            
            known_keys = [
                ('integration_time', 'Integration time', lambda x: '{}μs'.format(x)), 
                ('d0_start_time', 'Dark frames start time (before)', lambda x: self._to_html_field(x)),
                ('d0_end_time', 'Dark frames end time (before)', lambda x: self._to_html_field(x)),
                ('d1_start_time', 'Dark frames start time (after)', lambda x: self._to_html_field(x)),
                ('d1_end_time', 'Dark frames end time (after)', lambda x: self._to_html_field(x)),
            ]
            
            for k, text, format_function in known_keys:
                if k not in data.keys():
                    continue
                r += ['<tr><td><b>{}</b></td><td>{}</td></tr>'.format(text, format_function(data[k]))]
                klist.remove(k)
                
            if 'data_positions' in klist:
                klist.remove('data_positions')
                v = []
                for t in sorted(data['data_positions'].keys()):
                    v.append('{}: {} {}'.format(str(t), data['data_positions'][t][0], {True: '(M)',}.get(data['data_positions'][t][1], '')))
                text = '<br>'.join(v)
                    
                r += ['<tr><td><b>Scan positions</b></td><td>{}</td></tr>'.format(text)]
                
                
            for k in klist:
                r += ['<tr><td><b>{}</b></td><td>{}</td></tr>'.format(k, pprint.pformat(data[k]))]
            
            r += ['<table>']
            
            return ''.join(r)
        elif type(data) == list and key == 'processing_steps':
            r = ['<table border=1 width="100%">']
            for mod, rev, options in data:
                r += ['<tr><td><b>{}</b></td><td>{}</td></tr>'.format(mod, self._to_html_field(rev))]
                r += ['<tr><td colspan=2>{}</td></tr>'.format(options)]
            
            r += ['<table>']
            return ''.join(r)
        elif type(data) == dict:
            r = ['<table border=1 width="100%">']
            for k in data.keys():
                r += ['<tr><td><b>{}</b></td><td>{}</td></tr>'.format(str(k), pprint.pformat(data[k]))]
            
            r += ['<table>']
            return ''.join(r)
        elif key == 'wavelengths':
            r = ['<table border=1 width="100%">']
            for band_id, center_wavelength in enumerate(data):
                r += ['<tr><td><b>Band {}</b></td><td>{}nm</td></tr>'.format(band_id, center_wavelength)]
            
            r += ['<table>']
            return ''.join(r)
        else:
            return pprint.pformat(data)
        
    def _to_html_field(self, data):
        if type(data) == bytes:  #Specific formats
            return data.decode('utf-8')
        else:
            return str(data)        
            
    def fileQuit(self):
        self.close()

    def closeEvent(self, ce):
        self.fileQuit()

