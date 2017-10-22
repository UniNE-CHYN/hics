from PyQt4 import QtGui, QtCore
from .ui.focus import Ui_Focus
import redis
import numpy

class FocusWindow(QtGui.QWidget, Ui_Focus):
    closed = QtCore.pyqtSignal()
    resizable = False
    
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.slPosition.valueChanged.connect(self._slot_position_changed)
        self.slPosition.sliderMoved.connect(self._slot_position_moved)
        self.slPosition.sliderPressed.connect(self._slot_position_pressed)
        self.slPosition.sliderReleased.connect(self._slot_position_released)
        
        self.sbFrom.valueChanged.connect(self._slot_from_changed)
        self.sbTo.valueChanged.connect(self._slot_to_changed)
        
        self._position_pressed = False
        self._valid_focus = False
        self.focus_changed()
        
    def closeEvent(self, event):
        self.closed.emit()
        
    def _slot_position_pressed(self):
        self._position_pressed = True
    
    def _slot_position_released(self):
        self._position_pressed = False
        
    def _slot_position_moved(self, value):
        self.lbPosition.setText(str(value))
        
    def _slot_position_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.publish('hics:focus:move_absolute', value)
        
    def _slot_from_changed(self, value):
        self.slPosition.blockSignals(True)
        self.slPosition.setMinimum(value)
        self.slPosition.blockSignals(False)
        self.sbTo.setMinimum(value)
        
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.set('hics:focus:range_from', value)
        redis_client.publish('hics:focus', 'range_from')
        
    def _slot_to_changed(self, value):
        self.slPosition.blockSignals(True)
        self.slPosition.setMaximum(value)
        self.slPosition.blockSignals(False)
        self.sbFrom.setMaximum(value)
        
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.set('hics:focus:range_to', value)
        redis_client.publish('hics:focus', 'range_to')
        
    def focus_changed(self):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        
        range_from = redis_client.get('hics:focus:range_from')
        range_to = redis_client.get('hics:focus:range_to')
        state = redis_client.get('hics:focus:state')
        
        if state is not None:
            moving, position = [int(x) for x in state.decode('ascii').split(':')]
        
            if range_from is None:
                range_from = position
            if range_to is None:
                range_to = position
            
        self._valid_focus = range_from is not None and range_to is not None and state is not None
        
        if self._valid_focus:
            range_from = int(range_from)
            range_to = int(range_to)
            moving, position = [int(x) for x in state.decode('ascii').split(':')]
            
            if not self.sbFrom.hasFocus() or self.sbFrom.property('readOnly'):
                self.sbFrom.blockSignals(True)
                self.sbFrom.setValue(range_from)
                self.sbFrom.blockSignals(False)
                self.slPosition.blockSignals(True)
                self.slPosition.setMinimum(range_from)
                self.slPosition.blockSignals(False)
                self.sbTo.setMinimum(range_from)
                
            if not self.sbTo.hasFocus() or self.sbTo.property('readOnly'):
                self.sbTo.blockSignals(True)
                self.sbTo.setValue(range_to)
                self.sbTo.blockSignals(False)
                
                self.slPosition.blockSignals(True)
                self.slPosition.setMaximum(range_to)
                self.slPosition.blockSignals(False)
                self.sbFrom.setMaximum(range_to)
            
            if not self._position_pressed:
                self.slPosition.blockSignals(True)
                self.slPosition.setValue(position)
                self.slPosition.blockSignals(False)
                self.lbPosition.setText(str(position))
                
        step_size = 10 ** max(0, numpy.floor(numpy.log10(numpy.abs(self.sbTo.value() - self.sbFrom.value()))) - 2)
        self.slPosition.setSingleStep(step_size)
        self.slPosition.setPageStep(10*step_size)
            
        self.lock_status_changed(self.parent().window().locked)

    def lock_status_changed(self, locked):
        read_only = not locked or not self._valid_focus
        self.sbFrom.setReadOnly(read_only)
        self.sbTo.setReadOnly(read_only)
        self.slPosition.setEnabled(not read_only)

