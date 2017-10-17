from PyQt4 import QtGui, QtCore
from .ui.camera import Ui_Camera
import redis

class CameraWindow(QtGui.QWidget, Ui_Camera):
    closed = QtCore.pyqtSignal()
    resizable = False
    
    def __init__(self, *args, **kwargs):
        QtGui.QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self._valid_camera = False
        
        self.camera_changed()
        
        self.sbFrameRate.valueChanged.connect(self._slot_frame_rate_changed)
        self.sbIntegrationTime.valueChanged.connect(self._slot_integration_time_changed)
        self.sbNuc.valueChanged.connect(self._slot_nuc_changed)
        self.cbShutterOpen.stateChanged.connect(self._slot_shutteropen_changed)
        
        self.sbFrameRate.editingFinished.connect(self._field_lost_focus)
        self.sbIntegrationTime.editingFinished.connect(self._field_lost_focus)
        self.sbNuc.editingFinished.connect(self._field_lost_focus)
        #self.cbShutterOpen.editingFinished.connect(self._field_lost_focus)
        
    def closeEvent(self, event):
        self.closed.emit()
        
    def _slot_integration_time_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.publish('hics:camera:integration_time', value)
    
    def _slot_frame_rate_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.publish('hics:camera:frame_rate', value)
        
    def _slot_nuc_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        redis_client.publish('hics:camera:nuc', value)
        
    def _slot_shutteropen_changed(self, value):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        if value == 2:
            redis_client.publish('hics:camera:shutter_open', '1')
        else:
            redis_client.publish('hics:camera:shutter_open', '0')
        
    def _field_lost_focus(self):
        self.camera_changed()
        
        
    def camera_changed(self):
        redis_client = self.parent().window()._redis_client
        assert isinstance(redis_client, redis.client.Redis)
        
        integration_time = redis_client.get('hics:camera:integration_time')
        frame_rate = redis_client.get('hics:camera:frame_rate')
        nuc = redis_client.get('hics:camera:nuc')
        shutter_open = redis_client.get('hics:camera:shutter_open')
        
        self._valid_camera = integration_time is not None and frame_rate is not None and nuc is not None
        
        if self._valid_camera:
            integration_time = float(integration_time)
            frame_rate = int(frame_rate)
            nuc = int(nuc)
            shutter_open = int(shutter_open) == 1
            
            if not self.sbFrameRate.hasFocus() or self.sbFrameRate.property('readOnly'):
                self.sbFrameRate.blockSignals(True)
                self.sbFrameRate.setValue(frame_rate)
                self.sbFrameRate.blockSignals(False)
            if not self.sbIntegrationTime.hasFocus() or self.sbIntegrationTime.property('readOnly'):
                self.sbIntegrationTime.blockSignals(True)
                self.sbIntegrationTime.setValue(integration_time)
                self.sbIntegrationTime.blockSignals(False)
            if not self.sbNuc.hasFocus() or self.sbNuc.property('readOnly'):
                self.sbNuc.blockSignals(True)
                self.sbNuc.setValue(nuc)
                self.sbNuc.blockSignals(False)
            if not self.cbShutterOpen.hasFocus() or self.cbShutterOpen.property('readOnly'):
                self.cbShutterOpen.blockSignals(True)
                self.cbShutterOpen.setChecked(shutter_open)
                self.cbShutterOpen.blockSignals(False)
            
        self.lock_status_changed(self.parent().window().locked)
        
    def lock_status_changed(self, locked):
        read_only = not locked or not self._valid_camera
        
        self.sbFrameRate.setReadOnly(read_only)
        self.sbIntegrationTime.setReadOnly(read_only)
        self.sbNuc.setReadOnly(read_only)
        self.cbShutterOpen.setDisabled(read_only)
