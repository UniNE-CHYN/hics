import pickle

import numpy
import os

from hics.utils.plugin import BaseImperativePlugin
class AutoScan(BaseImperativePlugin):
    plugin_name = 'Auto-scan'
    plugin_key = 'autoscan'
    plugin_input = []
    plugin_output = []
    plugin_output_captions =  []
    
    plugin_uses = ['hics:scanner:range_from', 'hics:scanner:range_to']
    plugin_listens = ['hics:plugin:notification', 'hics:scanner:state']
    plugin_requires_lock = True
    
    plugin_input_before = [
        'string:/data/collection',
        'string:' + '',  #override number
        'string:' + '1000,2000,3000',  #integration times
        'integerspinbox:-4096000:4096000:0',
        'integerspinbox:-4096000:4096000:0',
        'integerspinbox:-4096000:4096000:0',
    ]
    plugin_input_before_captions = [
        'Data storage directory',
        'Sample ID (empty for auto)', 
        'Integration times',
        'Scan from', 
        'Scan to',
        'White frame position',
    ]
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
    
    def start(self):
        self._folder = self._input_before[0].decode('utf8').strip()
        self._sample_id = self._input_before[1].decode('utf8').strip()
        self._integration_times = self._input_before[2].decode('utf8').strip()
        self._scan_from = int(self._input_before[3].decode('utf8').strip())
        self._scan_to = int(self._input_before[4].decode('utf8').strip())
        self._white_frame_position = int(self._input_before[5].decode('utf8').strip())
        self._print_label = False
        
        if len(self._sample_id) != 4:
            self._print_label = True
            for i in range(10000):
                if not os.path.exists(os.path.join(self._folder, '{:04}'.format(i))):
                    break
            
            self._sample_id = '{:04}'.format(i)
            
        self._workdir = os.path.join(self._folder, self._sample_id)
        if not os.path.isdir(self._workdir):
            os.mkdir(self._workdir)
            
        #We're cheating, we don't really require a lock
        self._lock.release()
        
        super().start()
        
    def call_plugin(self, plugin_name, *args):
        assert all(type(a) == bytes for a in args)
        for a_id, a in enumerate(args):
            self._redis_client.publish('hics:plugin:{}:input_before:{}'.format(plugin_name, a_id), a)
        self._redis_client.publish('hics:plugin:{}'.format(plugin_name), 'start')
        self._running_plugins.add(plugin_name)
        
    def wait_for_plugins_completion(self):
        while not self._stop and len(self._running_plugins) > 0:
            key, data = self._queue.get()
            if key == 'hics:plugin:notification':
                pl_name, pl_action = data.decode('utf8').split(':')
                if pl_name in self._running_plugins and pl_action == 'stop':
                    self._running_plugins.remove(pl_name)
                    
    def _run(self):
        self._running_plugins = set()
        
        #Initial setup
        self._redis_client.publish("hics:camera:nuc", "0")
        self._redis_client.publish("hics:camera:integration_time", "3000")
        self._redis_client.publish("hics:scanner:range_from", self._scan_from)
        self._redis_client.publish("hics:scanner:range_to", self._scan_to)
        
        self.move_to(int((self._scan_from+self._scan_to) /2))
        self.call_plugin('autofocus', b'30')
        self.wait_for_plugins_completion()
        
        self.move_to(self._white_frame_position)
        
        record_params = [
            self._workdir.encode('utf8'), 
            self._integration_times.encode('utf8'), 
            b'',  #Focus positions
            b'0',  #Dark frame time
            b'1',  #White frame time
            b'',  #Scan times
            b'Automatic scan'
        ]        
        self.call_plugin('record', *record_params)
        self.wait_for_plugins_completion()
        
        
        if self._print_label:
            self.call_plugin('labelprint', b"192.168.1.6", b'1', b'N', self._sample_id.encode('ascii'))
            self.wait_for_plugins_completion()
    
if __name__ == '__main__':
    AutoScan.main()


