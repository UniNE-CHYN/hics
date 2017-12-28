import pickle

import numpy


from hics.utils.plugin import BaseImperativePlugin
class AutoFocus(BaseImperativePlugin):
    plugin_name = 'Auto-focus'
    plugin_key = 'autofocus'
    plugin_input = []
    plugin_output = ['livegraph']
    plugin_output_captions =  ['Live contrast']
    
    plugin_uses = []
    plugin_listens = ['hics:framegrabber:frame', 'hics:focus:state', 'hics:focus:velocity']
    plugin_requires_lock = True
    
    plugin_input_before = []
    plugin_input_before_captions = []
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._frame_rate = 100        
    
    def start(self):
        super().start()
    
    def _run(self):
        pos_1 = int(self._redis_client.get('hics:focus:range_from'))
        pos_2 = int(self._redis_client.get('hics:focus:range_to'))
        
        npts = 100
        
        current_position = None
        focus_data = {}
        
        last_integration_time = None
        while not self._stop:
            key, data = self._queue.get()
            print(key)
            if key == 'hics:framegrabber:frame':
                matrix = pickle.loads(data)
                matrix_avg = numpy.average(matrix, 1)
            
                m = (numpy.abs((matrix[1:] - matrix[:-1]))/matrix.mean()).sum()
                self.output_post(0, m)
                if current_position is not None:
                    focus_data[current_position] = m
                    
            elif key == 'hics:focus:state':
                print(data)
                state = [int(x) for x in data.split(b':')]
                moving = state[0] == 1
                current_position = state[1]
                direction = 0
                
            
                if current_position >= pos_2:
                    direction = -1
                elif current_position <= pos_1:
                    direction = 1
                else:
                    k = numpy.array(list(focus_data.keys()))
                    i = numpy.abs(k-current_position).argsort()[:npts]
                    data_x = k[i]
                    data_y = [focus_data[x] for x in data_x]
                    print(data_x, data_y)
                    if len(data_x) >= 2:
                        direction = numpy.polyfit(data_x, data_y, 1)[0]
                        direction = int(direction / numpy.abs(direction))
                    elif not moving:
                        direction = numpy.random.choice([-1, 1])
                        
                if direction != 0:
                    print(direction)
                    if direction == 1:
                        self._redis_client.publish('hics:focus:move_absolute', pos_2)
                    elif direction == -1:
                        self._redis_client.publish('hics:focus:move_absolute', pos_1)
        print("STOP")
    
if __name__ == '__main__':
    AutoFocus.main()
