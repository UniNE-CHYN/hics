from PyQt4 import QtGui, QtCore
import numpy
import time
import redis
import functools
import os


from .ui.mainwindow import Ui_MainWindow
from .camera import CameraWindow
from .scanner import ScannerWindow
from .focus import FocusWindow
from .cameraoutput import CameraOutputWindow
from .waterfall import WaterfallWindow
from .qredislistener import RedisListener
from ..utils.redis import RedisLock
from .widgets.glplotcanvas import GLPlotCanvas
from .plugin import Plugin

class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    lock_status_change = QtCore.pyqtSignal(bool)
    
    _plugin_check_interval = 1  #s
    
    def __init__(self, *args, **kwargs):
        settings = QtCore.QSettings()
        
        QtGui.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        
        self._plugins = {}
        
        if 'REDIS_URL_OVERRIDE' in os.environ:
            self._redis_url = os.environ['REDIS_URL_OVERRIDE']
        else:
            self._redis_url = settings.value('redis/url', 'redis://127.0.0.1:6379')
        
        self._redis_client = redis.from_url(self._redis_url)
        assert isinstance(self._redis_client, redis.client.Redis)
        try:
            self._redis_client.ping()
        except Exception as e:
            import traceback, sys
            msgbox = QtGui.QMessageBox()
            msgbox.setText("Couldn't connect to Redis!")
            msgbox.setInformativeText(traceback.format_exc(chain=False))
            msgbox.setIcon(QtGui.QMessageBox.Critical)
            msgbox.exec_()
            
            from .settings import SettingsWindow
            sw = SettingsWindow(self)
            sw.exec_()
            
            sys.exit(1)
            
        
        self._redislistener = RedisListener(self._redis_client)
        self._redislistener.start()
        
        
        
        self._redis_lock = RedisLock(self._redis_client, 'hics:lock', 'qtapp')
        if not self._redis_lock.acquire(False):
            msgbox = QtGui.QMessageBox()
            msgbox.setText("Unable to acquire hics:lock. Is another QtApp running somewhere?")
            msgbox.setIcon(QtGui.QMessageBox.Critical)
            msgbox.exec_()
        
        self.lock_status_change.connect(self.lock_status_changed)
        self.actionLocked.triggered.connect(self._action_locked)
        
        self.lock_status_change.emit(self.locked)
        
        #Menus
        self.actionExportData.triggered.connect(self._action_export_data)
        self.actionSettings.triggered.connect(self._action_settings)
        self.actionSaveState.triggered.connect(self._action_save_state)
        self.actionLoadState.triggered.connect(self._action_load_state)
        
        self.actionQuit.triggered.connect(self.close)
        self.actionCameraControlShow.triggered.connect(self._action_camera_control_show)
        self.actionScannerControlShow.triggered.connect(self._action_scanner_control_show)
        self.actionFocusControlShow.triggered.connect(self._action_focus_control_show)
        self.actionCameraOutputShow.triggered.connect(self._action_camera_output_show)
        
        self.actionMagnitudeWaterfallShow.triggered.connect(self._action_magnitude_waterfall_show)
        
        self.actionExportData.setEnabled(False)
        self.mdiArea.subWindowActivated.connect(self._active_window_change)
        
        #Handle plugins
        self._redislistener.plugin_announce_received.connect(self._plugin_announce_received)
        self._redislistener.plugin_notification_received.connect(self._plugin_notification_received)
        self._redislistener.plugin_output_received.connect(self._plugin_output_received)
        self._redislistener.plugin_output_after_received.connect(self._plugin_output_after_received)
        self._update_plugins_timer = QtCore.QTimer(self)
        self._update_plugins_timer.timeout.connect(self._update_plugins)
        self._update_plugins_timer.start(self._plugin_check_interval * 1000.)
        self._update_plugins()

        
    @property
    def locked(self):
        return self._redis_lock.lock_acquired
    
    def lock(self):
        self._redis_lock.acquire(blocking=True)
        self.lock_status_change.emit(self.locked)
        
    def unlock(self):
        self._redis_lock.release()
        self.lock_status_change.emit(self.locked)
        
    def lock_status_changed(self, value):
        self.actionLocked.setChecked(value)
        for plugin in self._plugins.values():
            plugin._qaction_update()
        
    def _action_load_state(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, "Load state", None, "State file (*.hsccstate)");
        if filename == '':
            return
        
        for l in open(filename, 'r').read().split('\n'):
            k, val = l.split(' ', 1)
            self._redis_client.publish(k, val)
            
        
    def _action_save_state(self):
        filename = QtGui.QFileDialog.getSaveFileName(self, "Save state", None, "State file (*.hsccstate)");
        if filename == '':
            return
        
        data = []
        for k in ('hics:camera:frame_rate', 'hics:camera:integration_time', 'hics:camera:nuc', 'hics:scanner:range_from', 'hics:scanner:range_to', 'hics:scanner:velocity'):
            data.append('{0} {1}'.format(k, self._redis_client.get(k).decode('ascii')))
        
        open(filename, 'w').write('\n'.join(data))
        
    def _action_new_magnitude_view(self):
        from .widgets.mplcanvas import MplCanvas
        window = self.mdiArea.addSubWindow(MplCanvas(self))
        window.show()
        
    def _active_window_change(self, win):
        if win is None:
            self.actionExportData.setEnabled(False)
        else:
            self.actionExportData.setEnabled(hasattr(win.widget(), "export_data"))
        
    def _action_export_data(self):
        win = self.mdiArea.activeSubWindow()
        assert win is not None
        data = win.widget().export_data()
        
        filename = QtGui.QFileDialog.getSaveFileName(self, "Export data", None, "Python files (*.py)");
        if filename == '':
            return
        
        open(filename, 'w').write('# {0}\n\n{1}\n'.format(self.mdiArea.windowTitle(), data))
        
        
        
    def _action_locked(self, checked):
        if checked:
            self.lock()
        else:
            self.unlock()
        
    def _unique_window_show(self, control_var, close_function, window_cls, checked):
        control_var_value = getattr(self, control_var, None)
        if self and control_var_value is None:
            window = self.mdiArea.addSubWindow(window_cls(self))
            window.widget().closed.connect(close_function)
            if window.widget().resizable:
                window.resize(window.sizeHint())
            else:
                window.setFixedSize(window.sizeHint())
                window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowMinimizeButtonHint & ~QtCore.Qt.WindowMaximizeButtonHint)
            window.show()
            
            if hasattr(window.widget(), 'lock_status_changed'):
                self.lock_status_change.connect(window.widget().lock_status_changed)
                #Call for first initialization
                window.widget().lock_status_changed(self.locked)
            
            setattr(self, control_var, window)
            return True
        elif not checked and control_var_value is not None:
            control_var_value.close()
            return False
        return None
            
    def _unique_window_close(self, control_var, menuopt):
        control_var_value = getattr(self, control_var, None)
        assert control_var_value is not None
        
        if hasattr(control_var_value.widget(), 'lock_status_changed'):
            self.lock_status_change.disconnect(control_var_value.widget().lock_status_changed)
        
        self.mdiArea.removeSubWindow(control_var_value)
        menuopt.setChecked(False)
        setattr(self, control_var, None)   
    
        
    def _action_camera_control_show(self, checked):
        ret = self._unique_window_show('_camera_control_window', self._camera_control_close, CameraWindow, checked)
        if ret is True:
            self._redislistener.camera_changed.connect(self._camera_control_window.widget().camera_changed)
            
    def _camera_control_close(self):
        self._redislistener.camera_changed.disconnect(self._camera_control_window.widget().camera_changed)
        self._unique_window_close('_camera_control_window', self.actionCameraControlShow)
        
    def _action_scanner_control_show(self, checked):
        ret = self._unique_window_show('_scanner_control_window', self._scanner_control_close, ScannerWindow, checked)
        if ret is True:
            self._redislistener.scanner_changed.connect(self._scanner_control_window.widget().scanner_changed)
            
    def _action_focus_control_show(self, checked):
        ret = self._unique_window_show('_focus_control_window', self._focus_control_close, FocusWindow, checked)
        if ret is True:
            self._redislistener.focus_changed.connect(self._focus_control_window.widget().focus_changed)
        
            
    def _scanner_control_close(self):
        self._redislistener.scanner_changed.disconnect(self._scanner_control_window.widget().scanner_changed)
        self._unique_window_close('_scanner_control_window', self.actionScannerControlShow)
        
    def _focus_control_close(self):
        self._redislistener.focus_changed.disconnect(self._focus_control_window.widget().focus_changed)
        self._unique_window_close('_focus_control_window', self.actionFocusControlShow)
        
        
    def _action_camera_output_show(self, checked):
        ret = self._unique_window_show('_camera_output_window', self._camera_output_close, CameraOutputWindow, checked)
        if ret is True:
            self._redislistener.hypcam_picture_received.connect(self._camera_output_window.widget().hypcam_picture_received)        
            
    def _camera_output_close(self):
        self._redislistener.hypcam_picture_received.disconnect(self._camera_output_window.widget().hypcam_picture_received)        
        self._unique_window_close('_camera_output_window', self.actionCameraOutputShow)
        
    def _action_magnitude_waterfall_show(self, checked):
        ret = self._unique_window_show('_magnitude_waterfall_window', self._magnitude_waterfall_close, WaterfallWindow, checked)
        if ret is True:
            self._redislistener.hypcam_picture_received.connect(self._magnitude_waterfall_window.widget().hypcam_picture_received)        
            
    def _magnitude_waterfall_close(self):
        self._redislistener.hypcam_picture_received.disconnect(self._magnitude_waterfall_window.widget().hypcam_picture_received)        
        self._unique_window_close('_magnitude_waterfall_window', self.actionMagnitudeWaterfallShow)

        
    def _action_webcam_output_show(self, checked):
        ret = self._unique_window_show('_webcam_output_window', self._webcam_output_close, WebcamOutputWindow, checked)
        if ret is True:
            self._redislistener.webcam_picture_received.connect(self._webcam_output_window.widget().webcam_picture_received)
            
    def _webcam_output_close(self):
        self._redislistener.webcam_picture_received.disconnect(self._webcam_output_window.widget().webcam_picture_received)
        self._unique_window_close('_webcam_output_window', self.actionWebcamOutputShow)
        
    def _action_datamanagement_show(self, checked):
        ret = self._unique_window_show('_datamanagement_window', self._datamanagement_close, DataManagementWindow, checked)
        if ret is True:
            pass

        
    def _action_settings(self):
        from .settings import SettingsWindow
        sw = SettingsWindow(self)
        sw.exec_()    
        
        
    def _close(self):
        self.close()
        
    def closeEvent(self, event):
        self.mdiArea.closeAllSubWindows()
        if self.mdiArea.currentSubWindow():
            event.ignore()
        else:
            event.accept()
            if self._redis_lock.lock_acquired:
                self._redis_client.publish('hics:scanner:move_absolute', 0)
                
            print("Stopping threads...")
            #Wait for the thread to stop
            self._redislistener.stop()
            self._redislistener.wait()
            self._redis_lock.stop()
            print("Done!")
            
    def _update_plugins(self, send_redis = True):
        if send_redis:
            self._redis_client.publish('hics:plugin', 'discover')
            
        #Refresh state
        for item in self._plugins.values():
            item.refresh_state_from_redis()
            
        #Remove expired plugins
        self._plugins = dict(item for item in self._plugins.items() if not item[1].expired)
        
        cur_menu_entries = set(self.menuPlugins.actions())
        new_menu_entries = set([x._qaction for x in self._plugins.values()])
        
        if cur_menu_entries != new_menu_entries:
            self.menuPlugins.clear()
            for action in sorted(new_menu_entries, key = lambda x:x.text()):
                self.menuPlugins.addAction(action)

    def _plugin_announce_received(self, k):
        expire_in = self._update_plugins_timer.interval() / 1000. * 5.
        
        if k not in self._plugins:
            self._plugins[k] = Plugin(self, k, expire_in)
            self._update_plugins(False)
        else:
            self._plugins[k].expire_in(expire_in)
        
    def _plugin_notification_received(self, data):
        plugin_key, message = data.split(':', 1)
        self._plugins[plugin_key].notification_received(message)
        
    def _plugin_output_received(self, plugin_key, output_id, data):
        self._plugins[plugin_key].output_received(output_id, data)
        
    def _plugin_output_after_received(self, plugin_key, output_id, data):
        self._plugins[plugin_key].output_after_received(output_id, data)
    
        
        
        
if __name__ == "__main__":
    import sys
    QtCore.QCoreApplication.setOrganizationName("Université de Neuchâtel")
    QtCore.QCoreApplication.setOrganizationDomain("unine.ch")
    QtCore.QCoreApplication.setApplicationName("HyperSpectral Camera Controller")
    
    app = QtGui.QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec_())


    
