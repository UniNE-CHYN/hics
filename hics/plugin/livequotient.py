import numpy
import time
import datetime
import sys
import os
import tempfile
import time

numpy.seterr(all = 'raise')

from hics.utils.plugin import BaseImperativePlugin


class LiveQuotient(BaseImperativePlugin):
    plugin_name = 'Live quotient'
    plugin_key = 'livequotient'
    plugin_input = []
    plugin_output = ['livespectrum']  #livegraph:[number of seconds]
    plugin_output_captions = ['quotient at half frame']

    plugin_uses = ['hics:camera:nuc', 'hics:camera:shutter_open']
    plugin_listens = ['hics:framegrabber:frame_raw', 'hics:scanner:state']
    plugin_requires_lock = False

    plugin_input_before = []
    plugin_input_before_captions = []

    _debug = False
    


    def start(self):
        self._redis_client.publish('hics:camera:nuc', 0)
        
        super().start()

    def stop(self):
        return  #do nothing
    
    def _run(self):
        frames = []
        
        #Get dark frame
        self._redis_client.publish('hics:camera:shutter_open', 0)
        time.sleep(2)
        dark_frame = self.get_frame()[:, 0, :].astype(numpy.float)
        self._redis_client.publish('hics:camera:shutter_open', 1)
        time.sleep(2)
        
        #Drop all previous frames...    
        self.get_frame(True)
        f_initial = (self.get_frame(False)[:, 0, :].astype(numpy.float) - dark_frame)
        
        
        pos = f_initial.shape[0]//2 + 1
        
        while not self._stop:
            matrix = (self.get_frame(False)[:, 0, :].astype(numpy.float) - dark_frame)
            
            data = matrix[pos] / f_initial[pos]
            data /= numpy.percentile(data, 90)
            self.output_post(0, ','.join(str(x) for x in data))
            


if __name__ == '__main__':
    LiveQuotient.main()
