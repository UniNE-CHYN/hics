import numpy
import time
import datetime
import sys
import os
import tempfile
import time

numpy.seterr(all = 'raise')

from hics.utils.plugin import BaseImperativePlugin


class LiveRefl(BaseImperativePlugin):
    plugin_name = 'Live reflectance'
    plugin_key = 'liverefl'
    plugin_input = []
    plugin_output = ['livespectrum']  #livegraph:[number of seconds]
    plugin_output_captions = ['reflectance 60/240']

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
        while not self._stop:
            matrix = (self.get_frame(False)[:, 0, :].astype(numpy.float) - dark_frame)
            matrix_avg = numpy.average(matrix, 1)
            
            data = matrix[60] / matrix[320-60]
            print(data.shape)
            self.output_post(0, ','.join(str(x) for x in data))
            


if __name__ == '__main__':
    LiveRefl.main()
