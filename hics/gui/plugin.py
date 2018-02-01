import time
import functools
from PyQt4 import QtCore, QtGui

class PluginOutputLivegraph:
    def __init__(self, parent_plugin, output_title, specification):
        self._parent_plugin = parent_plugin
        self._output_title = output_title
        self._window = None
        if len(specification) > 0:
            self._timed_value_expiration = float(specification[0])
        else:
            self._timed_value_expiration = None
        
    def start(self):
        from .widgets.glplotcanvas import GLPlotCanvas
        window = self._parent_plugin._mainwindow.mdiArea.addSubWindow(GLPlotCanvas(self._parent_plugin._mainwindow))
        window.resize(200, 200)
        
        window.setWindowTitle('{0}: {1}'.format(self._parent_plugin._name, self._output_title))
        window.show()
        self._window = window
        
        if self._timed_value_expiration is not None:
            window.widget().timed_value_expiration = self._timed_value_expiration 
            
        window.destroyed.connect(functools.partial(self._parent_plugin._output_window_closed, self))
        
    def new_data(self, data):
        if self._window is None:
            return
        output_widget = self._window.widget()
        output_widget.add_timed_value(float(data))        
        
    
    def stop(self):
        if self._window is None:
            return

        self._window.destroyed.disconnect()
        self._window.close()
        self._window = None
        
    def window_closed(self):
        self._window = None
        
class PluginOutputLivespectrum:
    def __init__(self, parent_plugin, output_title, specification):
        self._parent_plugin = parent_plugin
        self._output_title = output_title
        self._window = None
        
    def start(self):
        from .widgets.glplotcanvas import GLPlotCanvas
        window = self._parent_plugin._mainwindow.mdiArea.addSubWindow(GLPlotCanvas(self._parent_plugin._mainwindow))
        window.resize(200, 200)
        
        window.setWindowTitle('{0}: {1}'.format(self._parent_plugin._name, self._output_title))
        window.show()
        self._window = window
            
        window.destroyed.connect(functools.partial(self._parent_plugin._output_window_closed, self))
        
    def new_data(self, data):
        if self._window is None:
            return
        output_widget = self._window.widget()
        output_widget._y_max = 1.2
        output_widget._y_min = 0        
        output_widget.update_plot([float(x) for x in data.split(b',')])        
        
    
    def stop(self):
        if self._window is None:
            return

        self._window.destroyed.disconnect()
        self._window.close()
        self._window = None
        
    def window_closed(self):
        self._window = None
        
class PluginOutputProgress:
    def __init__(self, parent_plugin, output_title, specification):
        self._parent_plugin = parent_plugin
        self._output_title = output_title
        self._window = None
        assert len(specification) == 0

    def start(self):
        from .widgets.progresswidget import ProgressWidget
        window = self._parent_plugin._mainwindow.mdiArea.addSubWindow(ProgressWidget(self._parent_plugin._mainwindow))
        window.resize(400, 100)

        window.setWindowTitle('{0}: {1}'.format(self._parent_plugin._name, self._output_title))
        window.show()
        self._window = window

        window.destroyed.connect(functools.partial(self._parent_plugin._output_window_closed, self))

    def new_data(self, data):
        if self._window is None:
            return
        output_widget = self._window.widget()
        percentage, message = data.decode('utf8').split(':', 1)
        
        output_widget.percentage = int(percentage)
        output_widget.text = message

    def stop(self):
        if self._window is None:
            return

        self._window.destroyed.disconnect()
        self._window.close()
        self._window = None

    def window_closed(self):
        self._window = None
        
class PluginOutputAfterXYGraph:
    def __init__(self, parent_plugin, output_title, specification):
        self._parent_plugin = parent_plugin
        self._output_title = output_title
        assert len(specification) == 0
        
    def render(self, data):
        from .widgets.glplotcanvas import GLPlotCanvas
        window = self._parent_plugin._mainwindow.mdiArea.addSubWindow(GLPlotCanvas(self._parent_plugin._mainwindow))
        window.resize(200, 200)
        
        window.setWindowTitle('{0}: {1}'.format(self._parent_plugin._name, self._output_title))
        window.show()
        
        x_data, y_data = data.decode('ascii').split('/')
        x_data = [float(x) for x in x_data.split(',')]
        y_data = [float(y) for y in y_data.split(',')]
        output_widget = window.widget()
        output_widget.update_plot(x_data, y_data)
        
        
class InputWindow:
    def __init__(self, parent_plugin, widget, before = False):
        self._parent_plugin = parent_plugin
        
        self._widget = widget
        self._before = before
        
        if before:
            self._basekey = 'hics:plugin:{0}:input_before'.format(self._parent_plugin._key)
        else:
            self._basekey = 'hics:plugin:{0}:input'.format(self._parent_plugin._key)
            
        self._fields = self._parent_plugin._redis_client.get(self._basekey).decode('ascii').split(' ')
        if self._fields == ['']:
            self._fields = []
        self._fields_caption = [self._parent_plugin._redis_client.get(self._basekey + ':{0}'.format(i)).decode('utf8') for i in range(len(self._fields))]
        
        self._qt_fields = []
        
        formlayout = QtGui.QFormLayout(self._widget)
        
        for i in range(len(self._fields)):
            lbl = QtGui.QLabel(self._widget)
            lbl.setText(self._fields_caption[i])
            
            formlayout.setWidget(i, QtGui.QFormLayout.LabelRole, lbl)
            
            field_spec = self._fields[i].split(':', 1)
            if len(field_spec) == 1:
                f = getattr(self, "get_field_{0}".format(field_spec[0]))(i, '')
            else:
                f = getattr(self, "get_field_{0}".format(field_spec[0]))(i, field_spec[1])
            formlayout.setWidget(i, QtGui.QFormLayout.FieldRole, f)
            self._qt_fields.append(f)
        
        if before:
            buttonBox = QtGui.QDialogButtonBox(self._widget)
            buttonBox.setOrientation(QtCore.Qt.Horizontal)
            buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
            formlayout.setWidget(len(self._fields), QtGui.QFormLayout.SpanningRole, buttonBox)
            buttonBox.accepted.connect(self.accepted)
            buttonBox.rejected.connect(self.rejected)
        else:
            for i in range(len(self._fields)):
                field_spec = self._fields[i].split(':', 1)
                field_qt = self._qt_fields[i]
                if hasattr(self, '_connect_{0}'.format(field_spec[0])):
                    getattr(self, '_connect_{0}'.format(field_spec[0]))(field_qt, i)
                else:
                    self._connect(field_spec[0], field_qt, i)
                field_qt.valueChanged.connect(functools.partial(self._input_changed, i))
        #QtCore.QMetaObject.connectSlotsByName(self._widget)
        
    def get_field_integerspinbox(self, input_id, args):
        sb_min, sb_max, sb_default = [int(x) for x in args.split(':')]
        
        default_override = self._parent_plugin._input_get(input_id)
        if default_override is not None:
            sb_default = int(default_override)
        
        sb = QtGui.QSpinBox(self._widget)
        sb.setMinimum(sb_min)
        sb.setMaximum(sb_max)
        sb.setValue(sb_default)
        return sb
    
    def get_value_integerspinbox(self, field, args):
        return '{0}'.format(field.value()).encode('ascii')
    
    def get_field_string(self, input_id, args):
        te_default = args
        
        default_override = self._parent_plugin._input_get(input_id)
        if default_override is not None:
            te_default = default_override.decode('utf8')

        te = QtGui.QTextEdit(self._widget)
        te.setText(te_default)
        return te

    def get_value_string(self, field, args):
        return '{0}'.format(field.toPlainText()).encode('utf8')
    
    def _connect(self, field_type, field_qt, field_id):
        field_qt.valueChanged.connect(functools.partial(self._input_changed, field_id))
        self._input_changed(field_id)
    
    def widget(self):
        return self._widget
    
    def _input_changed(self, input_id):
        field_spec = self._fields[input_id].split(':', 1)
        field_qt = self._qt_fields[input_id]
        
        if len(field_spec) == 1:
            value = getattr(self, "get_value_{0}".format(field_spec[0]))(field_qt, '')
        else:
            value = getattr(self, "get_value_{0}".format(field_spec[0]))(field_qt, field_spec[1])
            
        self._parent_plugin._input_save(input_id, value)
        self._parent_plugin._redis_client.publish(self._basekey + ':{0}'.format(input_id), value)
        
        
        
    
    def accepted(self):
        for i in range(len(self._fields)):
            field_spec = self._fields[i].split(':', 1)
            field_qt = self._qt_fields[i]
            if len(field_spec) == 1:
                value = getattr(self, "get_value_{0}".format(field_spec[0]))(field_qt, '')
            else:
                value = getattr(self, "get_value_{0}".format(field_spec[0]))(field_qt, field_spec[1])
                
            self._parent_plugin._input_save(i, value)
            self._parent_plugin._redis_client.publish(self._basekey + ':{0}'.format(i), value)
        
        self._widget.done(1)
    
    def rejected(self):
        self._widget.done(0)
        
    
    

class Plugin(QtCore.QObject):
    started = QtCore.pyqtSignal()
    stopped = QtCore.pyqtSignal()
    
    output_type_mapping = {'livegraph': PluginOutputLivegraph, 'livespectrum': PluginOutputLivespectrum, 'progress': PluginOutputProgress,}
    output_after_type_mapping = {'xygraph': PluginOutputAfterXYGraph, }
    
    redis_latency = 2  #Maximum time to propagate the change of state in redis
    _redis_last_change = None
    
    def __init__(self, mainwindow, key, expire_in):
        QtCore.QObject.__init__(self)
        self._mainwindow = mainwindow
        self._redis_client = mainwindow._redis_client
        
        self._key = key
        self._name = self._redis_client.get('hics:plugin:{0}'.format(self._key)).decode('utf8')
        self._requires_lock = (self._redis_client.get('hics:plugin:{0}:requires_lock'.format(self._key)) == b'1')
        self._expire_at = expire_in + time.time()
        
        self._input = self._redis_client.get('hics:plugin:{0}:input'.format(self._key)).decode('ascii').split(' ')
        if self._input == ['']:
            self._input = []
        self._input_before = self._redis_client.get('hics:plugin:{0}:input_before'.format(self._key)).decode('ascii').split(' ')
        if self._input_before == ['']:
            self._input_before = []
            
        self._input_saved = {}
        
        #Outputs
        self._outputs = []
        for output in self._redis_client.get('hics:plugin:{0}:output'.format(self._key)).decode('ascii').split(' '):
            if output == '':
                continue
            output_parameters = output.split(':')
            output_type, output_parameters_split = output_parameters[0], output_parameters[1:]
            if len(output_parameters_split) == 1 and output_parameters_split[0] == '':
                output_parameters_split = []
                
            output_title = self._redis_client.get('hics:plugin:{0}:output:{1}'.format(self._key, len(self._outputs))).decode('utf8')
                
            self._outputs.append(self.output_type_mapping[output_type](self, output_title, output_parameters_split))
            
        #Outputs after
        self._outputs_after = []
        for output in self._redis_client.get('hics:plugin:{0}:output_after'.format(self._key)).decode('ascii').split(' '):
            if output == '':
                continue
            output_parameters = output.split(':')
            output_type, output_parameters_split = output_parameters[0], output_parameters[1:]
            if len(output_parameters_split) == 1 and output_parameters_split[0] == '':
                output_parameters_split = []
                
            output_title = self._redis_client.get('hics:plugin:{0}:output_after:{1}'.format(self._key, len(self._outputs_after))).decode('utf8')
                
            self._outputs_after.append(self.output_after_type_mapping[output_type](self, output_title, output_parameters_split))
            
        
        self._input_window = None
        self._output_windows = {}
        
        self._qaction = QtGui.QAction(self._mainwindow)
        self._qaction.setCheckable(True)
        self._qaction.setText(self._name)
        self._qaction.triggered.connect(self._qaction_triggered)
        
        #state = 0: stopped, 1: starting, 2: started, 3: stopping
        if self._redis_client.get('hics:plugin:{0}:running'.format(self._key)) == b'1':
            self._state = 1
            self.started()
        else:
            self._state = 0
        
        self._qaction_update()
        
    @property
    def name(self):
        return self._name
    
    @property
    def expired(self):
        #It's expired if it's not stopped and we didn't see anything
        return self.state == 0 and self._expire_at < time.time()
    
    @property
    def state(self):
        return self._state
    
    @state.setter
    def state(self, new_value):
        assert new_value in (0, 1, 2, 3)
        self._state = new_value
        self._redis_last_change = time.time()
        self._qaction_update()
    
    def expire_in(self, nseconds):
        self._expire_at = time.time() + nseconds
        
    def start(self):
        """This function asks for *before data,
        sends the start signal to the plugin, and releases the lock."""
        
        assert self.state == 0
        
        if len(self._input_before):
            inputwindow = InputWindow(self, QtGui.QDialog(self._mainwindow), True)
            inputwindow.widget().setWindowTitle(self._name)
            ret = inputwindow.widget().exec_()
            if ret == 0:
                self._qaction_update()
                return
            
        #start
        self._redis_client.publish('hics:plugin:{0}'.format(self._key), 'start')
        if self._requires_lock:
            #release lock
            self._mainwindow.unlock()
            
        self.state = 1
    
    def started(self):
        """Called when the plugin is started"""
        #assert self.state == 1
        
        self._qaction.setChecked(True)
        
        #FIXME: input, output
        if len(self._input) > 0:
            inputwindow = InputWindow(self, QtGui.QWidget(self._mainwindow), False)
            window = self._mainwindow.mdiArea.addSubWindow(inputwindow.widget())
            window.setWindowTitle(self._name)
            window.show()
            
            self._input_window = window
            self._input_window.destroyed.connect(self._input_window_closed)
            
        
        
        for output in self._outputs:
            output.start()
                
        self.state = 2
    
    def stop(self):
        """This function sends the stop signal and acquires the lock"""
        if self.state in (0, 3):  #Stopped or stopping: do nothing
            return
        
        #We can stop both in starting state or in running state
        assert self.state in (1, 2)
        
        #stop
        self._redis_client.publish('hics:plugin:{0}'.format(self._key), 'stop')
        
        self.state = 3
        
        if self._requires_lock:
            #acquire lock
            self._mainwindow.lock()
    
    def stopped(self):
        """Called when the plugin is stopped, and show the *after data"""
        if self.state in (1, 2):
            if self._requires_lock:
                #acquire lock
                self._mainwindow.lock()
            self.state = 3
            
        #assert self.state == 3
        
        self._qaction.setChecked(False)
                
        if self._input_window is not None:
            self._input_window.destroyed.disconnect()
            self._input_window.close()
            self._input_window = None
        
        for output in self._outputs:
            output.stop()
            
        #FIXME: output_after
        
        self.state = 0
        
    def _qaction_triggered(self, checked):
        if checked:
            self.start()
        else:
            self.stop()
            
        pass
    
    def _qaction_update(self):
        self._qaction.setChecked(self.state != 0)
        
        #We can active this QAction if (one required):
        #- we're holding the lock
        #- this plugin is running (we should always be able to stop it)
        #- this plugin doesn't require lock (can always be run)
        self._qaction.setEnabled(self._mainwindow.locked or self.state != 0 or not self._requires_lock)
        
    def _input_window_closed(self):
        self._input_window = None
        self.stop()
        
    def _output_window_closed(self, output):
        output.window_closed()
        self.stop()
        
    def output_received(self, output_id, data):
        self._outputs[output_id].new_data(data)
        
    def output_after_received(self, output_id, data):
        self._outputs_after[output_id].render(data)
        #p = PluginOutputAfterXYGraph(self, '', [])
        #p.render(data)
        
    def refresh_state_from_redis(self):
        if self.state in (1, 2, 3):
            if self._redis_last_change is not None and self._redis_last_change + self.redis_latency >= time.time():
                return
                
            if self._redis_client.get('hics:plugin:{0}:running'.format(self._key)) != b'1':
                self.stopped()
        
    def notification_received(self, message):
        if message == 'stop':
            self.stopped()
        elif message == 'start':
            self.started()
            
    def _input_save(self, input_id, value):
        self._input_saved[input_id] = value
        
    def _input_get(self, input_id):
        return self._input_saved.get(input_id, None)
    
        
        
