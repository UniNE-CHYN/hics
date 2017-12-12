from PyQt5 import QtCore, QtWidgets

from mmappickle import mmapdict, httpdict

import numpy
import pprint

import re
import queue
import functools
import time
import os
import copy

import matplotlib
# Make sure that we are using QT5
matplotlib.use('Qt5Agg')
from PyQt5 import QtCore, QtWidgets

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

import scipy.interpolate
import os

class PChipNormalize(matplotlib.colors.Normalize):
    def __init__(self, points):
        xi = [x[0] for x in points]
        yi = [x[1] for x in points]
        
        self._xs = numpy.linspace(xi[0], xi[-1], 1000)
        self._ys = numpy.clip(scipy.interpolate.pchip_interpolate(xi, yi, self._xs), 0, 1)
        
        matplotlib.colors.Normalize.__init__(self, xi[0], xi[-1], True)
        

    def __call__(self, value, clip=None):
        return numpy.ma.masked_array(numpy.interp(value, self._xs, self._ys), numpy.ma.getmask(value))
    
class HicsData(QtCore.QObject):
    """This object is immutable and represent a data series in a file"""
    def __init__(self, filename, key, dimensions_list, value_unit, avg_func='mean'):
        super().__init__()
        self._m = mmapdict(filename, True)
        self._filename = filename
        self._key = key
        #List of dimentions
        self._dimensions_list = tuple(dimensions_list)
        self._value_unit = value_unit
        self._avg_func = avg_func
        
        self._data = self._m[self._key]
        
        if self._key + '-var' in self._m.keys():
            self._var = self._m[self._key+'-var']
        else:
            self._var = None
            
    @property
    def axes(self):
        return self._dimensions_list
    
    @property
    def data_ref(self):
        return (os.path.abspath(self._filename), self._key)
    
    def get_dimension(self, axis):
        #FIXME: other special cases?
        return self._data.shape[self._dimensions_list.index(axis)]
    
    def get_ticks(self, axis):
        if axis == 'l':
            return self._m['wavelengths']
        #FIXME: other special cases?
        return numpy.arange(self._data.shape[self._dimensions_list.index(axis)])
            
    def __at(self, data_coordinates=None, return_axes_order=None, on='_data'):
        if data_coordinates is None:
            data_coordinates = {}
        data_indexes = [data_coordinates.get(x, slice(None, None)) for x in self._dimensions_list]
        
        data = getattr(self, on)[data_indexes]
        
        if return_axes_order is not None:
            return_indexes = [i for i, v in enumerate(data_indexes) if type(v) in (slice, list, tuple)]
            assert len(return_indexes) == data.ndim
            return_axes_order = [self._dimensions_list.index(x) for x in return_axes_order]
            
            return_axes_all = return_axes_order + [x for x in return_indexes if x not in return_axes_order]
            data = data.transpose([return_indexes.index(i) for i in return_axes_all])
            
            if len(return_axes_order) != len(return_axes_all):
                data = getattr(data, self._avg_func)(axis=tuple(range(len(return_axes_order), len(return_axes_all))))
            
        if hasattr(data, 'mask'):
            return data
        else:
            return numpy.ma.masked_invalid(data)
            
            
    def data_at(self, data_coordinates=None, return_axes_order=None):
        return self.__at(data_coordinates, return_axes_order, '_data')
    
    def var_at(self, data_coordinates=None, return_axes_order=None):
        if self._var is None:
            return numpy.ma.zeros_like(self.__at(data_coordinates, return_axes_order, '_data'))
        return self.__at(data_coordinates, return_axes_order, '_var')
    

class HicsDataView(QtCore.QObject):
    viewChanged = QtCore.pyqtSignal(name='viewChanged')
    
    def __init__(self, **kw):
        super().__init__()
        

        self._data = None
        #Defaults
        self._spatial_axes = ['y', 'x']
        self._data_axis = 'l'
        self._cnorm_points = {}
        
        self._display_bands = dict([(x, None) for x in 'rgb'])
        self._display_points = dict([(x, None) for x in matplotlib.rcParams['axes.prop_cycle'].by_key()['color']])
        
        
        self.__cache_data_to_display = None
        
        #FIXME: use explicit keys, to avoid issues with the order of the set...
        for k, v in kw.items():
            setattr(self, k, v)
            
        
            
    def _changed(self, data_changed=True):
        if data_changed:
            self.__cache_data_to_display = None
        if self.valid:
            self.viewChanged.emit()        
    
    @property
    def valid(self):
        if self._data is None:
            return False
        
        for k in self._spatial_axes:
            if k not in self._data.axes:
                return False
            
        if self.data_axis not in self._data.axes:
            return False
        return True
        
    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, newvalue):
        assert isinstance(newvalue, HicsData)
        self._data = newvalue
        self._changed(data_changed=True)

            
    
    @property
    def display_bands(self):
        return self._display_bands.copy()
    
    def display_bands_set(self, k, value):
        if k not in self._display_bands.keys():
            raise KeyError(k)
        
        if not (0 <= value < self.data.get_dimension(self._data_axis)):
            raise ValueError("{} is out of bounds for {}".format(value, self._data_axis))
        
        self._display_bands[k] = value
        self._changed(data_changed=True)
        
    @property
    def display_points(self):
        return self._display_points.copy()
    
    def display_points_set(self, k, p):
        if k not in self._display_points.keys():
            raise KeyError(k)
        
        assert type(p) == dict
        assert all(x in self.data.axes for x in p.keys())
        #FIXME: check points
        
        self._display_points[k] = p
        self._changed()   
        
        
    @property
    def spatial_axes(self):
        return self._spatial_axes.copy()
    
    @spatial_axes.setter
    def spatial_axes(self, newvalue):
        assert isinstance(newvalue, list)
        self._spatial_axes = newvalue.copy()
        self._changed(data_changed=True)      
        
    @property
    def data_axis(self):
        return self._data_axis
    
    @data_axis.setter
    def data_axis(self, newvalue):
        assert isinstance(newvalue, str)
        self._data_axis = newvalue
        self._changed(data_changed=True)
            
            
    @property
    def data_to_display(self):
        if self.__cache_data_to_display is not None:
            return self.__cache_data_to_display
        bands = self.display_bands
        if all(x is None for x in bands.values()):
            data_all = self.data.data_at({}, self.spatial_axes)
        else:
            bands_list = [bands['r'], bands['g'], bands['b']]
            data = self.data.data_at({self.data_axis: [x for x in bands_list if x is not None],}, self.spatial_axes+[self.data_axis])
            
            #Fill to get always all the bands
            data_all = numpy.ma.masked_all(data.shape[:-1] + (len(bands_list), ))
            b = 0
            for target_band_id, band in enumerate(bands_list):
                if band is not None:
                    data_all[:, :, target_band_id] = data[:, :, b]
                    b += 1
                
        self.__cache_data_to_display = data_all
        return data_all
    
    def data_for_band(self, band_id):
        if band_id is None:
            return self.data.data_at({}, self.spatial_axes)
        else:
            return self.data.data_at({self.data_axis: band_id}, self.spatial_axes)
        
    @property
    def cnorm_points(self):
        #Color normalization points
        #returns a dict: 
        # key: (data.data_ref, data_axis coordinate) -> point list
        # if data_axis_coordinate is None, then it's for the average
        return copy.deepcopy(self._cnorm_points)
    
    @cnorm_points.setter
    def cnorm_points(self, newvalue):
        #No checks, be careful here!
        self._cnorm_points = newvalue.copy()
        if self.valid:
            self.viewChanged.emit()        
    
    def cnorm_points_get(self, data_idx):
        key = (self.data.data_ref, data_idx)
        
        if key not in self._cnorm_points:
            #Generate a standard 1-99 percentile color normalization
            if data_idx is not None:
                data = self.data.data_at({self.data_axis: data_idx}, self.spatial_axes).compressed()
            else:
                data = self.data.data_at({}, self.spatial_axes).compressed()
                
            if len(data) == 0:
                points = [(0, 0), (1, 1)]
            else:
                points = [(data.min(), 0), (numpy.percentile(data, 1), 0), (numpy.percentile(data, 99), 1), (data.max(), 1)]            
            
            self._cnorm_points[key] = points
            
        return self._cnorm_points[key].copy()
    
    def cnorm_points_set(self, data_idx, points):
        key = (self.data.data_ref, data_idx)
        self._cnorm_points[key] = points
        self._changed(data_changed=False)     
    
    def cnorm_get(self, data_idx):
        return PChipNormalize(self.cnorm_points_get(data_idx))
        
    @property
    def cm(self):
        return matplotlib.cm.get_cmap('jet')
    
    def get_ax_extent(self, ax):
        ticks = self.data.get_ticks(ax)
        return (ticks.min(), ticks.max())
        

class HicsDataView_(QtCore.QObject):
    viewChanged = QtCore.pyqtSignal(name='viewChanged')
    
    def __init__(self, filename, key, dimlist, dimfunctions=None, normpoints=None):
        super().__init__()
        #TMP
        test = HicsData(filename, key, dimlist, 'DN')
        print(test.data_at({}, ['x', 'l', 'y']).shape)
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
        if self._key + '-var' in self._m.keys():
            self._var = self._m[self._key+'-var']
        else:
            self._var = None
                
        self._normpoints = normpoints
        if self._normpoints is None:
            self._normpoints = []
            
    @property
    def data_to_display(self):
        indexes = [{None: slice(None, None), 'mean': slice(None, None), 'median': slice(None, None)}.get(k, k) for k in self._dimfunctions]
        d = self._data
        for f_id, f in reversed(list(enumerate(self._dimfunctions))):
            if type(f) == None:
                continue
            elif type(f) == tuple:
                new_shape = list(d.shape)
                new_shape[f_id] = len(f)
                new_d = numpy.ma.masked_all(new_shape)
                for new_idx, old_idx in enumerate(f):
                    if old_idx is None:
                        continue
                    old_idx_full = [slice(None, None)] * f_id + [old_idx] + [Ellipsis]
                    new_idx_full = [slice(None, None)] * f_id + [new_idx] + [Ellipsis]
                    new_d[new_idx_full] = d[old_idx_full]
                
                d = new_d
            elif type(f) == str:
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
    
    def var_at(self, x, y):
        indexes = [{'x': x, 'y': y}.get(k, slice(None, None)) for k in self._dimlist]
        if self._var is None:
            return None
        else:
            return self._var[indexes]
    
    def get_normpoints(self, data_idx):
        while len(self._normpoints) < data_idx + 1:
            self._normpoints.append([])
            
        if len(self._normpoints[data_idx]) == 0:
            vd = self.data_to_display
            if vd.ndim == 2:
                assert data_idx == 0
                vd = vd[:, :, numpy.newaxis]
            assert vd.ndim == 3
            
            dimdata = vd[:, :, data_idx]
            
            if hasattr(dimdata, 'compressed'):
                dimdata = dimdata.compressed()
            else:
                dimdata = dimdata.flatten()
            
            if len(dimdata) == 0:
                self._normpoints[data_idx] = [(0, 0), (1, 1)]
            else:
                self._normpoints[data_idx] = [(dimdata.min(), 0), (numpy.percentile(dimdata, 1), 0), (numpy.percentile(dimdata, 99), 1), (dimdata.max(), 1)]
        return self._normpoints[data_idx]
    
    def set_normpoints(self, data_idx, new_data):
        while len(self._normpoints) < data_idx + 1:
            self._normpoints.append([])
        self._normpoints[data_idx] = new_data
        self.viewChanged.emit()
        
    def get_norm(self, data_idx):
        return PChipNormalize(self.get_normpoints(data_idx))
    
    @property
    def cm(self):
        return matplotlib.cm.get_cmap('jet')
    
    @property
    def lastdim(self):
        return [dim_id for dim_id, k in enumerate(self._dimlist) if k not in ['x', 'y']][-1]
    
    def get_dataindex(self, color_index):
        if type(self._dimfunctions[self.lastdim]) != tuple:
            return None
        
        if color_index < len(self._dimfunctions[self.lastdim]):
            return self._dimfunctions[self.lastdim][color_index]
        
        return None
        
    def set_dataindex(self, color_index, matrix_index):
        if type(self._dimfunctions[self.lastdim]) != tuple:
            self._dimfunctions[self.lastdim] = (None, None, None)
        
        df = list(self._dimfunctions[self.lastdim])
        #FIXME: Save normalization
        df[color_index] = matrix_index
        df = tuple(df)
        if df == (None, None, None):
            df = 'mean'
        #FIXME: Restore normalization (or create a new one)
        
        self._dimfunctions[self.lastdim] = df
        self.viewChanged.emit()
        
