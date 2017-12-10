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

import scipy.interpolate

class PChipNormalize(matplotlib.colors.Normalize):
    def __init__(self, points):
        xi = [x[0] for x in points]
        yi = [x[1] for x in points]
        
        self._xs = numpy.linspace(xi[0], xi[-1], 1000)
        self._ys = numpy.clip(scipy.interpolate.pchip_interpolate(xi, yi, self._xs), 0, 1)
        
        matplotlib.colors.Normalize.__init__(self, xi[0], xi[-1], True)
        

    def __call__(self, value, clip=None):
        return numpy.ma.masked_array(numpy.interp(value, self._xs, self._ys), numpy.ma.getmask(value))

class HicsDataView(QtCore.QObject):
    normChanged = QtCore.pyqtSignal(name='normChanged')
    
    def __init__(self, filename, key, dimlist, dimfunctions=None, normpoints=None):
        super().__init__()
        self._m = mmapdict(filename, True)
        self._filename = filename
        self._key = key
        self._dimlist = dimlist
        self._dimfunctions = dimfunctions
        if dimfunctions is None:
            if len(self._dimlist) == 2:
                self._dimfunctions = [None, None]
            else:
                self._dimfunctions = [{'x': None, 'y': None}.get(k, 'mean') for k in self._dimlist]
        
        assert self._key in self._m
        assert self._m[self._key].ndim == len(dimlist)
    
        assert all(x in ('x', 'y', 'l', 'exp', 'abundance') for x in self._dimlist)
        self._data = self._m[self._key]
                
        self._normpoints = normpoints    
        if normpoints is None:
            vd = self.data_to_display
            if vd.ndim == 2:
                vd = vd[:, :, numpy.newaxis]
            assert vd.ndim == 3
            
            self._normpoints = []
            for dim_id in range(vd.shape[2]):
                dimdata = vd[:, :, dim_id]
                
                if hasattr(dimdata, 'compressed'):
                    dimdata = dimdata.compressed()
                else:
                    dimdata = dimdata.flatten()
                
                self._normpoints.append([(dimdata.min(), 0), (numpy.percentile(dimdata, 1), 0), (numpy.percentile(dimdata, 99), 1), (dimdata.max(), 1)])        
        
        

        print(self.data_to_display.shape)
        print(self.data_to_display_axes)
        print(self.data_at_axes)
        print('x')

    @property
    def data_to_display(self):
        indexes = [{None: slice(None, None), 'mean': slice(None, None), 'median': slice(None, None)}.get(k, k) for k in self._dimfunctions]
        d = self._data[indexes]
        for f_id, f in reversed(list(enumerate(self._dimfunctions))):
            if type(f) != str:
                continue
            d = getattr(d, f)(f_id)
        return d
    
    @property
    def data_to_display_axes(self):
        return [self._dimlist[i] for i, k in enumerate(self._dimfunctions) if k is None]
    
    @property
    def data_at_axes(self):
        return [k for k in self._dimlist if k not in ['x', 'y']]
    
    @property
    def wavelengths(self):
        return numpy.array(self._m['wavelengths'])
    
    def get_ax_extent(self, axn):
        if axn == 'l':
            return [self.wavelengths.min(), self.wavelengths.max()]
        return [0, self._data.shape[self._dimlist.index(axn)]]
        
    def data_at(self, x, y):
        indexes = [{'x': x, 'y': y}.get(k, slice(None, None)) for k in self._dimlist]
        return self._data[indexes]
    
    def get_normpoints(self, data_idx):
        while len(self._normpoints) < data_idx:
            self._normpoints.append([])
        return self._normpoints[data_idx]
    
    def set_normpoints(self, data_idx, new_data):
        while len(self._normpoints) < data_idx:
            self._normpoints.append([])
        self._normpoints[data_idx] = new_data
        self.normChanged.emit()
        
    def get_norm(self, data_idx):
        return PChipNormalize(self.get_normpoints(data_idx))
    
    @property
    def cm(self):
        return matplotlib.cm.get_cmap('jet')
