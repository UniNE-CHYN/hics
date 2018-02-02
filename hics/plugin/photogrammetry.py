
import pickle

import numpy
import os
import time

from hics.utils.plugin import BaseImperativePlugin
class Photogrammetry(BaseImperativePlugin):
    plugin_name = 'Photogrammetry'
    plugin_key = 'photogrammetry'
    plugin_input = []
    plugin_output = []
    plugin_output_captions =  []
    
    plugin_uses = []
    plugin_listens = ['hics:webcam', 'hics:rotater:state']
    plugin_requires_lock = True
    
    plugin_input_before = [
        'string:/tmp',
    ]
    plugin_input_before_captions = [
        'Data storage directory',
    ]
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
    
    def start(self):
        self._folder = self._input_before[0].decode('utf8').strip()
        
        super().start()
        
                    
        if not self._lock.lock_acquired:
            #We're cheating, we don't really require a lock
            self._lock.acquire()        
                    
    def _run(self):
        #Initial setup
        while True:
            k, v = self._queue.get()
            if k == 'hics:rotater:state':
                initial_position = int(v.decode('ascii').split(':')[1])
                break
            
        positions = numpy.linspace(0,360,37)
        
        for position in positions:
            position = int(position)
            abspos = position + initial_position
            self._redis_client.publish("hics:rotater:move_absolute", abspos)
            current_position = None
            c = 0
            while current_position != abspos:
                if c > 10:
                    self._redis_client.publish("hics:rotater:move_absolute", abspos)
                    c = 0
                c += 1
                k, v = self._queue.get()
                if k == 'hics:rotater:state':
                    current_position = int(v.decode('ascii').split(':')[1])
            
            #Clear queue
            while not self._queue.empty():
                _dummy = self._queue.get()
                
            key = None
            while key != 'hics:webcam':
                key, data = self._queue.get()
            open(os.path.join(self._folder, 'im-{0:03d}.jpg'.format(position)), 'wb').write(data)
    
if __name__ == '__main__':
    Photogrammetry.main()


