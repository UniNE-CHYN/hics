from PyQt4 import QtGui, QtCore
from .ui.scanner import Ui_Scanner
import redis

class ScannerWindow(QtGui.QWidget, Ui_Scanner):
    closed = QtCore.pyqtSignal()
    resizable = False
    
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.slPosition.valueChanged.connect(self._slot_position_changed)
        self.slPosition.sliderMoved.connect(self._slot_position_moved)
        self.slPosition.sliderPressed.connect(self._slot_position_pressed)
        self.slPosition.sliderReleased.connect(self._slot_position_released)
        
        self.sbSpeed.valueChanged.connect(self._slot_speed_changed)
        
        self.sbFrom.valueChanged.connect(self._slot_from_changed)
        self.sbTo.valueChanged.connect(self._slot_to_changed)
        
        self._position_pressed = False
        self._valid_scanner = False
        self.scanner_changed()
        
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
        redis_client.publish('hics:scanner:move_absolute', value)
        
    def _slot_from_changed(self, value):
        self.slPosition.blockSignals(True)
        self.slPosition.setMinimum(value)
        self.slPosition.blockSignals(False)
        self.sbTo.setMinimum(value)
        
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.set('hics:scanner:range_from', value)
        redis_client.publish('hics:scanner', 'range_from')
        
    def _slot_to_changed(self, value):
        self.slPosition.blockSignals(True)
        self.slPosition.setMaximum(value)
        self.slPosition.blockSignals(False)
        self.sbFrom.setMaximum(value)
        
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.set('hics:scanner:range_to', value)
        redis_client.publish('hics:scanner', 'range_to')
        
    def _slot_speed_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.publish('hics:scanner:velocity', value)
        
    def scanner_changed(self):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        
        velocity = redis_client.get('hics:scanner:velocity')
        range_from = redis_client.get('hics:scanner:range_from')
        range_to = redis_client.get('hics:scanner:range_to')
        state = redis_client.get('hics:scanner:state')
        
        self._valid_scanner = velocity is not None and range_from is not None and range_to is not None and state is not None
        
        if self._valid_scanner:
            velocity = float(velocity)
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
            
            if not self.sbSpeed.hasFocus():
                self.sbSpeed.blockSignals(True)
                self.sbSpeed.setValue(velocity)
                self.sbSpeed.blockSignals(False)
            
        self.lock_status_changed(self.parent().window().locked)

    def lock_status_changed(self, locked):
        read_only = not locked or not self._valid_scanner
        self.sbFrom.setReadOnly(read_only)
        self.sbTo.setReadOnly(read_only)
        self.slPosition.setEnabled(not read_only)
        self.sbSpeed.setReadOnly(read_only)
