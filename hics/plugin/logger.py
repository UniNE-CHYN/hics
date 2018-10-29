import numpy, os, tempfile

from hics.utils.plugin import BasePlugin

class Logger(BasePlugin):
    plugin_name = 'Logger'
    plugin_key = 'logger'
    plugin_input_before = [
        'string:' + os.path.join(tempfile.gettempdir(), 'logger'),
    ]
    plugin_input_before_captions = [
        'Data storage directory',
    ]

    plugin_input = []
    plugin_output = ['livegraph:30']  #livegraph:[number of seconds]
    plugin_output_captions = ['messages received']
    
    plugin_uses = []
    plugin_listens = ['hics:framegrabber:frame_raw', 'hics:scanner:state']
    plugin_requires_lock = False
    
    def start(self):
        self._n_received = 0
        self._directory = self._input_before[0].decode('utf8').strip()
        if not os.path.exists(self._directory):
            os.mkdir(self._directory)
            
        for f in os.listdir(self._directory):
            os.unlink(os.path.join(self._directory, f))
    
    def stop(self):
        return  #do nothing
    
    def data_received(self, channel, data):
        if channel == 'hics:framegrabber:frame_raw':
            open(os.path.join(self._directory, '{0:06d}.frame_raw.npy'.format(self._n_received)), 'wb').write(data)
        elif channel == 'hics:scanner:state':
            open(os.path.join(self._directory, '{0:06d}.scanner.state'.format(self._n_received)), 'wb').write(data)
            
        self._n_received += 1
        self.output_post(0, self._n_received)
        
        return True
    
if __name__ == '__main__':
    Logger.main()
