import numpy
import time
import datetime
import sys
import os
import tempfile
import time
import pickle

numpy.seterr(all = 'raise')

from hics.utils.plugin import BaseImperativePlugin

from mmappickle import mmapdict
from mmappickle.stubs import EmptyNDArray


class RecordScan(BaseImperativePlugin):
    plugin_name = 'Record while scanning'
    plugin_key = 'recordscan'
    plugin_input = []
    plugin_output = []
    plugin_output_captions = []

    plugin_uses = ['hics:camera:integration_time', 'hics:camera:nuc', 'hics:camera:shutter_open', 'hics:scanner:velocity', '#position']
    plugin_listens = ['hics:framegrabber:frame_raw', 'hics:scanner:state']
    plugin_requires_lock = True

    plugin_input_before = [
        'string:/data/scans',
        'string:' + '',  #'500,1000,2000,4000,6000,8000,12000,16000,20000',
        'string:' + '',  #'10000,0,-4000,-8000,-12000,-16000,-20000,-24000,-28000,-32000,-36000,-40000,-44000,-48000,-52000,-56000',
        'integerspinbox:0:300:0',
        'integerspinbox:0:300:5',
        'string:'
    ]
    plugin_input_before_captions = [
        'Data storage directory',
        'Integration times',
        'Focus positions', 
        'Dark frame time',
        'White frame time',
        'Scan description'
    ]

    _debug = False
    


    def start(self):
        self._directory = self._input_before[0].decode('utf8').strip()
        self._dark_frame_time = int(self._input_before[3].decode('utf8').strip())
        self._white_frame_time = int(self._input_before[4].decode('utf8').strip())
        self._integration_times = [float(x.strip()) for x in self._input_before[1].decode('utf8').split(',') if x != '']
        self._focus_positions = [int(x.strip()) for x in self._input_before[2].decode('utf8').split(',') if x != '']
        if not os.path.exists(self._directory):
            os.mkdir(self._directory)
            
        self._redis_client.publish('hics:camera:nuc', 0)
        
        self._scan_velocity = int(self._redis_client.get('hics:scanner:velocity'))
        self._range_from = int(self._redis_client.get('hics:scanner:range_from'))
        self._range_to = int(self._redis_client.get('hics:scanner:range_to'))
        
        self._description = self._input_before[5].decode('utf8')
        
        super().start()

    def stop(self):
        return  #do nothing
    
    def _capture_frames_dark(self, storage, prefix, frame_shape, dark_frames_count, dark_frame_store_stats):
        if dark_frames_count == 0:
            return None, None
        #Close shutter
        self._redis_client.publish('hics:camera:shutter_open', 0)
        
        #Create dark frames
        s = time.time()
        if not dark_frame_store_stats:
            storage[prefix] = EmptyNDArray((frame_shape[0], dark_frames_count, frame_shape[2]))
        s = 2 - time.time() + s
        if s > 0:
            time.sleep(s)
            
        start_time = datetime.datetime.now()
        
        if not dark_frame_store_stats:
            frames = storage[prefix]
        else:
            frames = numpy.empty((frame_shape[0], dark_frames_count, frame_shape[2]))
        
        idx = 0
        while idx < dark_frames_count:
            frames[:, idx, :] = self.get_frame()[:, 0, :]
            idx += 1
            
        if dark_frame_store_stats:
            storage[prefix+'-avg'] = numpy.average(frames, 1)
            storage[prefix+'-var'] = numpy.var(frames, 1)
            
        end_time = datetime.datetime.now()
        
        return start_time, end_time
        
    
    def _capture_frames(self, storage, prefix, frame_shape, dark_frames_count_before, dark_frames_count_after, data_frames_count = None, capture_end_position = None, reversed_scan = False, dark_frame_store_stats = False):
        d0_start_time = None
        d0_end_time = None
        d1_start_time = None
        d1_end_time = None
        
        d0_start_time, d0_end_time = self._capture_frames_dark(storage, prefix+'-d0', frame_shape, dark_frames_count_before, dark_frame_store_stats)
            
        #Capture data
        data_positions = {}
        
        if data_frames_count is not None:
            self._redis_client.publish('hics:camera:shutter_open', 1)
            s = time.time()
            storage[prefix] = EmptyNDArray((frame_shape[0], data_frames_count, frame_shape[2]))
            s = 2 - time.time() + s
            if s > 0:
                time.sleep(s)
            while not self._queue.empty():
                _dummy = self._queue.get()
            data_start_time = datetime.datetime.now()
            idx = 0
            while idx < data_frames_count:
                key, data = self._queue.get()
                if key == 'hics:framegrabber:frame_raw':
                    storage[prefix][:, idx, :] = pickle.loads(data)[:, 0, :]
                    idx += 1
                elif key == 'hics:scanner:state':
                    state = [int(x) for x in data.split(b':')]
                    moving = state[0] == 1
                    position = state[1]
                    data_positions[datetime.datetime.now()] = (position, moving)
               
            data_end_time = datetime.datetime.now()
            
        elif capture_end_position is not None:
            self._redis_client.publish('hics:camera:shutter_open', 1)
            time.sleep(2)
            #Size is not known...
            self._redis_client.publish('hics:scanner:move_absolute', capture_end_position)
            
            frames = []
            moving = False
            while len(frames) == 0 or moving:
                key, data = self._queue.get()
                if key == 'hics:framegrabber:frame_raw' and moving:
                    frames.append(pickle.loads(data))
                elif key == 'hics:scanner:state':
                    state = [int(x) for x in data.split(b':')]
                    moving = state[0] == 1
                    position = state[1]
                    data_positions[datetime.datetime.now()] = (position, moving)            
                    
            if not reversed_scan:
                frames.reverse()            
            storage[prefix] = numpy.concatenate(frames, 1)
            
        d1_start_time, d1_end_time = self._capture_frames_dark(storage, prefix+'-d1', frame_shape, dark_frames_count_after, dark_frame_store_stats)
            
        properties = {
            'integration_time': float(self._redis_client.get('hics:camera:integration_time').decode('utf8')),
            'd0_start_time': d0_start_time,
            'd0_end_time': d0_end_time,
            'd1_start_time': d1_start_time,
            'd1_end_time': d1_end_time, 
            'data_positions': data_positions
        }
        
        focus_state = self._redis_client.get('hics:focus:state')
        if focus_state is not None:
            properties['focus_position'] = float(focus_state.decode('utf8').split(':')[1])
        storage[prefix+'-p'] = properties

            
        
    
    def _run(self):
        frame_rate = int(self._redis_client.get('hics:camera:frame_rate'))
        frame_shape = self.get_frame().shape
        
        if self._dark_frame_time == 0:
            dark_frame_count = 1
            dark_frame_store_stats = False
        else:
            dark_frame_count = int(self._dark_frame_time * frame_rate)
            dark_frame_store_stats = self._dark_frame_time >= 0        
        
        data = mmapdict(os.path.join(self._directory, datetime.datetime.now().strftime('%Y%m%d%H%M%S') + '.scan'))
        data['description'] = self._description + '\n\n' + \
            '\n'.join('{}: {}'.format(k, str(v)) for k, v in zip(self.plugin_input_before_captions, self._input_before)) + '\n\n' + \
            'Frame rate: {}'.format(frame_rate) + '\n' + \
            'Frame shape: {0[0]}x{0[2]}'.format(frame_shape)
        
        data['wavelengths'] = [float(x) for x in self._redis_client.get('hics:framegrabber:wavelengths').decode('utf8').split(',')]
        
        if len(self._focus_positions) == 0:
            self._focus_positions = [None]
            
        if len(self._integration_times) == 0:
            self._integration_times = [None]        
        
        if self._white_frame_time > 0:
            for scan_idx, integration_time in enumerate(self._integration_times):
                if integration_time is not None:
                    self._redis_client.publish('hics:camera:integration_time', integration_time)
                    time.sleep(2)
                #Capture 1 dark frame before and after
                self._capture_frames(data, 'white-{:05d}'.format(scan_idx), frame_shape, 1, 1, data_frames_count= int(self._white_frame_time * frame_rate))
        
        scan_idx = 0
        for focus_position in self._focus_positions:
            if focus_position is not None:
                #FIXME: wait to settle position
                print("hics:focus:move_absolute", focus_position)
                self._redis_client.publish("hics:focus:move_absolute", focus_position)
                
            for integration_time in self._integration_times:
                if integration_time is not None:
                    self._redis_client.publish('hics:camera:integration_time', integration_time)
                
                moving, current_position = self.get_position()
                reversed_scan = numpy.abs(current_position - self._range_from) > numpy.abs(current_position - self._range_to)
                
                if reversed_scan:
                    self.move_to(self._range_to)
                    target_position = self._range_from
                else:
                    self.move_to(self._range_from)
                    target_position = self._range_to

                self._redis_client.publish('hics:scanner:velocity', self._scan_velocity)
                
                self._capture_frames(data, 'scan-{:05d}'.format(scan_idx), frame_shape, 
                                    dark_frame_count, dark_frame_count, capture_end_position = target_position,
                                    reversed_scan = reversed_scan,
                                    dark_frame_store_stats = dark_frame_store_stats)
                scan_idx += 1

        self._redis_client.publish('hics:camera:shutter_open', 1)


if __name__ == '__main__':
    RecordScan.main()




