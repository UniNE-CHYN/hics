import numpy
from hics.utils.plugin import BaseImperativePlugin

numpy.seterr(all = 'raise')

class FocusHelper(BaseImperativePlugin):
    plugin_name = 'Manual focus'
    plugin_key = 'focushelper'
    plugin_input = []
    plugin_output = ['livegraph:15']  #livegraph:[number of seconds]
    plugin_output_captions = ['contrast']

    plugin_uses = []
    plugin_listens = ['hics:framegrabber:frame']
    plugin_requires_lock = False

    plugin_input_before = []
    plugin_input_before_captions = []

    def start(self):
        super().start()

    def stop(self):
        return  #do nothing
    
    def _run(self):
        frames = []
        
        #Drop all previous frames...    
        self.get_frame(True)
        while not self._stop:
            matrix = self.get_frame(False)[:, 0, :].astype(numpy.float)
            matrix_avg = numpy.average(matrix, 1)
            
            m = (numpy.abs((matrix[1:] - matrix[:-1]))/matrix.mean()).sum()
            self.output_post(0, m)
            


if __name__ == '__main__':
    FocusHelper.main()



