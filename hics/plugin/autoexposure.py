import pickle

import numpy


from hics.utils.plugin import BaseImperativePlugin
class AutoExposure(BaseImperativePlugin):
    plugin_name = 'Auto-exposure'
    plugin_key = 'autoexposure'
    plugin_input = []
    plugin_output = ['livegraph']
    plugin_output_captions =  ['Live magnitude'] #['magnitude in function of integration time']
    
    plugin_uses = ['#position', 'hics:scanner:velocity']
    plugin_listens = ['hics:framegrabber:frame_raw', 'hics:scanner:state']
    plugin_requires_lock = True
    
    plugin_input_before = ['integerspinbox:0:100:99', 'integerspinbox:0:100:75', 'integerspinbox:0:100:85']
    plugin_input_before_captions = ['Percentile', 'Lowest acceptable magnitude', 'Highest acceptable magnitude']
    
    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self._percentile = None
        self._lowest_acceptable_magnitude = None
        self._highest_acceptable_magnitude = None
        self._frame_rate = 100

        self._magnitude_max = None
        
    
    def start(self):
        self._integration_time = float(self._redis_client.get('hics:camera:integration_time'))
        self._scan_velocity = int(self._redis_client.get('hics:scanner:velocity'))
        
        self._percentile = int(self._input_before[0])
        self._lowest_acceptable_magnitude = int(self._input_before[1])
        self._highest_acceptable_magnitude = int(self._input_before[2])
        
        super().start()
    
    def _run(self):
        pos_1 = int(self._redis_client.get('hics:scanner:range_from'))
        pos_2 = int(self._redis_client.get('hics:scanner:range_to'))
        pixel_max = float(self._redis_client.get('hics:framegrabber:max_pixel_value'))
        target_pos = None
        in_scan = False
        frames = []
        last_integration_time = None
        while True:
            key, data = self._queue.get()
            if key == 'hics:framegrabber:frame_raw' and in_scan:
                frames.append(pickle.loads(data))
            elif key == 'hics:scanner:state':
                state = [int(x) for x in data.split(b':')]
                moving = state[0] == 1
                position = state[1]
                
                if ((pos_1 == position or pos_2 == position) and target_pos is None) or \
                   (position == target_pos):
                    if in_scan:
                        #Require at least one frame
                        if len(frames) == 0:
                            continue
                        #Process frames
                        data = numpy.concatenate(frames, 1)
                        p = numpy.percentile(data, self._percentile) / pixel_max * 100
                        target_p = (self._lowest_acceptable_magnitude + self._highest_acceptable_magnitude) / 2
                        integration_time = float(self._redis_client.get('hics:camera:integration_time'))
                        integration_time_min = float(self._redis_client.get('hics:camera:integration_time_min'))
                        integration_time_max = float(self._redis_client.get('hics:camera:integration_time_max'))
                        new_integration_time = numpy.clip(
                            target_p / p * integration_time,
                            integration_time_min,
                            integration_time_max
                        )
                        if new_integration_time == last_integration_time:
                            break
                        last_integration_time = new_integration_time
                        
                        if p < self._lowest_acceptable_magnitude or p > self._highest_acceptable_magnitude:
                            self._redis_client.publish('hics:camera:integration_time', new_integration_time)
                        else:
                            break
                        
                    if pos_1 == position:
                        target_pos = pos_2
                    else:
                        target_pos = pos_1
                    frames = []
                    in_scan = True
                elif target_pos is None:
                    if abs(pos_1 - position) < abs(pos_2 - position):
                        target_pos = pos_1
                    else:
                        target_pos = pos_2
                        
                if in_scan:
                    self.move_absolute(target_pos, min_speed=self._scan_velocity, max_speed=self._scan_velocity)
                else:
                    self.move_absolute(target_pos)

    
            
    
if __name__ == '__main__':
    AutoExposure.main()

