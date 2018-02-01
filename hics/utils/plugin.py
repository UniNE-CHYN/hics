import redis
import time
import pickle
import threading
import numpy

from hics.utils.redis import RedisLock

from mmappickle import mmapdict
from mmappickle.stubs import EmptyNDArray
import datetime

class BasePlugin:
    #Name of the plugin (for the menu)
    plugin_name = 'Unnamed plugin'
    #Key of the plugin (in redis)
    plugin_key = 'unnamed'
    
    #input:
    #integerspinbox:min:max:default
    
    plugin_input_before = []  #Input values to ask before starting plugin
    plugin_input_before_captions = []
    plugin_output_after = []  #Output to display after starting plugin
    plugin_output_after_captions = []
    
    plugin_input = []
    plugin_input_captions = []
    
    plugin_output = []
    #livegraph:[number of seconds] (if number of seconds is omitted, contains all data)
    
    plugin_output_captions = []
    
    #when any of the output is closed, the master should send a stop signal
    
    plugin_uses = []  #list of redis keys which should be stored/published before/after run
    #Special values: #position
    
    plugin_listens = []
    
    plugin_requires_lock = True
    
    _watchdog_expire_at = None
    _watchdog_refresh_at = None
    _watchdog_default_expiration = 30
    
    def __init__(self, redis_client, *a, **kw):
        self._redis_client = redis_client
        assert isinstance(self._redis_client, redis.client.Redis)
        
        self._input_before = [None] * len(self.plugin_input_before)
        
        self._running = False
        
    @property
    def running(self):
        return self._running
    
    def run(self):
        self._pubsub = self._redis_client.pubsub()
        self._pubsub.subscribe('hics:plugin')
        self._pubsub.subscribe('hics:plugin:{0}'.format(self.plugin_key))
            
        for input_id in range(len(self.plugin_input_before)):
            self._pubsub.subscribe('hics:plugin:{0}:input_before:{1}'.format(self.plugin_key, input_id))
            
        for input_id in range(len(self.plugin_input)):
            self._pubsub.subscribe('hics:plugin:{0}:input:{1}'.format(self.plugin_key, input_id))
            
        assert len(self.plugin_input) == len(self.plugin_input_captions)
        assert len(self.plugin_output) == len(self.plugin_output_captions)
        
        #Not running!
        self._redis_client.delete('hics:plugin:{0}:running'.format(self.plugin_key))
        self._redis_client.set('hics:plugin:{0}:requires_lock'.format(self.plugin_key), {True: '1', False: '0'}[self.plugin_requires_lock])
        self._redis_client.set('hics:plugin:{0}:input'.format(self.plugin_key), ' '.join(self.plugin_input))
        self._redis_client.set('hics:plugin:{0}:input_before'.format(self.plugin_key), ' '.join(self.plugin_input_before))
        self._redis_client.set('hics:plugin:{0}:output'.format(self.plugin_key), ' '.join(self.plugin_output))
        self._redis_client.set('hics:plugin:{0}:output_after'.format(self.plugin_key), ' '.join(self.plugin_output_after))
        for i in range(len(self.plugin_input_captions)):
            self._redis_client.set('hics:plugin:{0}:input:{1}'.format(self.plugin_key, i), self.plugin_input_captions[i].encode('utf8'))
        for i in range(len(self.plugin_input_before_captions)):
            self._redis_client.set('hics:plugin:{0}:input_before:{1}'.format(self.plugin_key, i), self.plugin_input_before_captions[i].encode('utf8'))
        for i in range(len(self.plugin_output_captions)):
            self._redis_client.set('hics:plugin:{0}:output:{1}'.format(self.plugin_key, i), self.plugin_output_captions[i].encode('utf8'))
        for i in range(len(self.plugin_output_after_captions)):
            self._redis_client.set('hics:plugin:{0}:output_after:{1}'.format(self.plugin_key, i), self.plugin_output_after_captions[i].encode('utf8'))
        
        self._redis_client.set('hics:plugin:{0}'.format(self.plugin_key), self.plugin_name)  
        
        try:
            for item in self._pubsub.listen():
                #Stop plugin if it is not running any more
                if self.running and self.plugin_should_stop():
                    self.__plugin_stop()
                    
                    
                if item['type'] not in ('message', ):
                    continue
                
                channel = item['channel']
                if type(channel) == bytes:
                    channel = channel.decode('ascii')
                    
                message = item['data']
                
                if self._watchdog_expire_at is None or self._watchdog_refresh_at < time.time():
                    self.wake_watchdog()
                
                if channel == 'hics:plugin':
                    if message == b'discover':
                        self._redis_client.publish('hics:plugin:announce', self.plugin_key)
                    else:
                        print(item)
                    continue
                
                if channel == 'hics:plugin:{0}'.format(self.plugin_key):
                    if message == b'start':
                        self.__plugin_start()
                    elif message == b'stop':
                        self.__plugin_stop()
                    elif message == b'kill':
                        break
                    else:
                        print(item)
                    continue
                
                #Data from custom channel required by the plugin
                if channel in self.plugin_listens:
                    if self.running:
                        ret = self.data_received(channel, message)
                        if not ret:
                            self.__plugin_stop()
                    #otherwise ignore...
                    continue
                
                #Now only plugin-specific message should remain
                if not channel.startswith('hics:plugin:{0}:'.format(self.plugin_key)):
                    print(item)
                    continue
                
                #Handle input/input_before messages
                channel_parts = channel.split(':')
                if len(channel_parts) != 5:
                    print(item)
                    continue
                
                if channel_parts[3] == 'input':
                    input_id = int(channel_parts[4])
                    if self.running:
                        self.input_received(input_id, message)
                elif channel_parts[3] == 'input_before':
                    input_id = int(channel_parts[4])
                    self._input_before[input_id] = message
                else:
                    print(item)
                    continue
        except KeyboardInterrupt:
            pass
        
        self._redis_client.delete('hics:plugin:{0}'.format(self.plugin_key))
        for i in range(len(self.plugin_input_captions)):
            self._redis_client.delete('hics:plugin:{0}:input:{1}'.format(self.plugin_key, i))
        for i in range(len(self.plugin_input_before_captions)):
            self._redis_client.delete('hics:plugin:{0}:input_before:{1}'.format(self.plugin_key, i))

        for i in range(len(self.plugin_output_captions)):
            self._redis_client.delete('hics:plugin:{0}:output:{1}'.format(self.plugin_key, i))
        for i in range(len(self.plugin_output_after_captions)):
            self._redis_client.delete('hics:plugin:{0}:output_after:{1}'.format(self.plugin_key, i))            
            
        self._redis_client.delete('hics:plugin:{0}:output_after'.format(self.plugin_key))
        self._redis_client.delete('hics:plugin:{0}:output'.format(self.plugin_key))
        self._redis_client.delete('hics:plugin:{0}:input_before'.format(self.plugin_key))
        self._redis_client.delete('hics:plugin:{0}:input'.format(self.plugin_key))
        self._redis_client.delete('hics:plugin:{0}:requires_lock'.format(self.plugin_key))
        
    @classmethod
    def main(cls, arg_parser = None):
        import argparse, redis
        if arg_parser is None:
            parser = argparse.ArgumentParser()
        else:
            parser = arg_parser
        parser.add_argument("--redis", help="Redis URL")
        args = parser.parse_args()
        if args.redis is not None:
            r = redis.from_url(args.redis)
        else:
            r = redis.Redis()
            
        args_dict = dict(args._get_kwargs())
        del args_dict['redis']
        obj = cls(r, **args_dict)
        obj.run()
        
    def _plugin_listen_start(self):
        for c in self.plugin_listens:
            self._pubsub.subscribe(c)        

    def _plugin_listen_stop(self):
        for c in self.plugin_listens:
            self._pubsub.unsubscribe(c)        
        
    def __plugin_start(self):
        if self._running:
            return
        
        if self.plugin_requires_lock:
            self._lock = RedisLock(self._redis_client, 'hics:lock', self.plugin_key)
            self._lock.acquire()
            
        self._plugin_listen_start()
            
        self._saved_data = {}
        for key in self.plugin_uses:
            if key.startswith('#'):
                self._saved_data[key] = getattr(self, '_redis_save_{0}'.format(key[1:]))()
            else:
                self._saved_data[key] = self._redis_client.get(key)
            
        self._output_after = [None] * len(self.plugin_output_after)
        
        self.start()
        self._redis_client.set('hics:plugin:{0}:running'.format(self.plugin_key), '1')
        self._redis_client.publish("hics:plugin:notification", '{0}:start'.format(self.plugin_key))
        self._running = True
        self.wake_watchdog()
    
    def __plugin_stop(self):
        if not self._running:
            return
        self._running = False
        self.stop()
        
        self._redis_client.delete('hics:plugin:{0}:running'.format(self.plugin_key))
        self._redis_client.publish("hics:plugin:notification", '{0}:stop'.format(self.plugin_key))
        
        self._plugin_listen_stop()
        
        if self.plugin_requires_lock:
            self._lock.release()
            self._lock.stop()
            del self._lock

        for key in self.plugin_uses:
            if key.startswith('#'):
                getattr(self, '_redis_restore_{0}'.format(key[1:]))(self._saved_data[key])
                
        for key in self.plugin_uses:
            if not key.startswith('#'):
                self._redis_client.publish(key, self._saved_data[key])
            
        del self._saved_data
        
        for output_id in range(len(self.plugin_output_after)):
            if self._output_after[output_id] is not None:
                self._redis_client.publish("hics:plugin:{0}:output_after:{1}".format(self.plugin_key, output_id), self._output_after[output_id])
                
        #Clear input_before (for next run)
        self._input_before = [None] * len(self.plugin_input_before)
        
    def wake_watchdog(self, expiration = None):
        if expiration is None:
            expiration = self._watchdog_default_expiration
            
        if self.running:
            ret = self._redis_client.expire('hics:plugin:{0}:running'.format(self.plugin_key), expiration)
            if not ret:
                print("{0}: Watchdog failed!".format(self.plugin_key))
                self._redis_client.set('hics:plugin:{0}:running'.format(self.plugin_key), '1', ex = expiration)
            
            self._watchdog_expire_at = time.time() + expiration
            self._watchdog_refresh_at = time.time() + expiration / 2
        
    def plugin_should_stop(self):
        #This can be overriden to stop the plugin if the thread(s) have ended
        return False
        
    def start(self):
        raise NotImplementedError("Plugin should implement start()")
    
    def stop(self):
        raise NotImplementedError("Plugin should implement stop()")
    
    def data_received(self, channel, data):
        raise NotImplementedError("Plugin should implement data_received()")
    
    def data_received(self, channel, data):
        raise NotImplementedError("Plugin should implement data_received()")
    
    def input_received(self, input_id, data):
        raise NotImplementedError("Plugin should implement input_received()")
    
    def output_post(self, output_id, value):
        assert output_id < len(self.plugin_output)
        self._redis_client.publish("hics:plugin:{0}:output:{1}".format(self.plugin_key, output_id), value)
        self.wake_watchdog()
        
    def output_post_later(self, output_id, value):
        assert output_id < len(self.plugin_output_after)
        self._output_after[output_id] = value
        self.wake_watchdog()
        
    def _redis_save_position(self):
        scannerstate=self._redis_client.get('hics:scanner:state')
        if scannerstate is None:
            return None
        moving, position = scannerstate.decode('ascii').split(':', 1)
        return int(position)
    
    def _redis_restore_position(self, position):
        velocity = self._redis_client.get('hics:scanner:velocity')
        if position is not None:
            self.move_absolute(position)
        self._redis_client.set('hics:scanner:velocity', velocity)
        
    def move_absolute(self, position, min_speed = None, max_speed = None, current_position = None):
        if min_speed is None:
            min_speed = int(self._redis_client.get('hics:scanner:velocity_min'))
        if max_speed is None:
            max_speed = int(self._redis_client.get('hics:scanner:velocity_max'))
            
        speed = max_speed
        
        if current_position is not None:
            min_dt = 0.1
            if abs(position - current_position) / speed < min_dt:
                speed = abs(position - current_position) / min_dt
            
            #max_speed = max(min_speed, min(abs(position - current_position), max_speed))
            
        self._redis_client.publish('hics:scanner:velocity', int(speed))
        self._redis_client.publish('hics:scanner:move_absolute', int(position))
        
    def _parse_list_or_range(self, s, conversion_function):
        r = []
        for x in s.split(','):
            if x == '':
                continue
            x_parts = x.split(':')
            if len(x_parts) == 1:
                try:
                    r.append(conversion_function(x_parts[0]))
                except:
                    pass
            elif len(x_parts) == 2:
                try:
                    r += list(numpy.arange(conversion_function(x_parts[0]), conversion_function(x_parts[1])))
                except:
                    pass
            elif len(x_parts) == 3:
                try:
                    r += list(numpy.arange(
                        conversion_function(x_parts[0]),
                        conversion_function(x_parts[1]),
                        conversion_function(x_parts[2])
                    ))
                except:
                    pass  
        return r
        
class BaseWorkerPlugin(BasePlugin):
    plugin_input = []
    plugin_output = ['progress']
    plugin_output_captions = ['progress']

    plugin_uses = []
    plugin_listens = ['hics:framegrabber:frame_raw']
    plugin_requires_lock = False

    _debug = False
    
    def start(self):
        self._work_results = []
        
        self._work_thread = threading.Thread(target = self._run)
        self._work_thread.start()

    def stop(self):
        self._work_queue.clear()
        self._work_results = []
        
        if self._work_thread is not None:
            self._work_thread.join()
        self._work_thread = None
        
    def _run(self):
        total_executed = 0
        
        while len(self._work_queue) > 0:
            cur_job = self._work_queue.pop(0)
            
            percentage = int(100 * total_executed / (total_executed + len(self._work_queue) + 1))
            msg = '{0}:{1}'.format(percentage, cur_job[0])
            print(msg)
            self.output_post(0, msg)
            ret = cur_job[1](*cur_job[2:])
            self._work_results.append((cur_job, ret))
            self.wake_watchdog()
            total_executed += 1
            
        return True
            

    def data_received(self, channel, data):
        return self._work_thread is not None and self._work_thread.isAlive()
    
    def plugin_should_stop(self):
        return not (self._work_thread is not None and self._work_thread.isAlive())
    
class BaseImperativePlugin(BasePlugin):
    plugin_input = []
    plugin_output = []
    plugin_output_captions = []

    plugin_uses = []
    plugin_listens = ['hics:framegrabber:frame_raw']
    plugin_requires_lock = False

    _debug = False
    
    _max_integration_time = 25000
    _min_integration_time = 1
    _switching_wait_time = 3
    _switching_stable_frame_count = 3
    _switching_noise_tolerance = 0.1
    _switching_min_detectable_integration_time_step = 4000
    
    def start(self):
        import queue
        self._queue = queue.Queue()
        self._stop = False
        self._work_thread = threading.Thread(target = self._run)
        self._work_thread.start()

    def stop(self):
        self._stop = True
        
        if self._work_thread is not None:
            self._work_thread.join()
        self._work_thread = None
        
    def _run(self):
        return True
    
    def clear_queue(self):
        while not self._queue.empty():
            self._queue.get()

    def data_received(self, channel, data):
        self._queue.put((channel, data))
        return self._work_thread is not None and self._work_thread.isAlive()
    
    def get_frame(self, now = True):
        if now:
            self.clear_queue()
        
        while True:
            key, data = self._queue.get()
            if key != 'hics:framegrabber:frame_raw' and key != 'hics:framegrabber:frame':
                continue
            return pickle.loads(data)
        
    def get_position(self, now = True):
        if now:
            self.clear_queue()
        
        while True:
            key, data = self._queue.get()
            if key != 'hics:scanner:state':
                continue
            state = [int(x) for x in data.split(b':')]
            return state[0] == 1, state[1]
        
    def _switch_wait_luminosity(self, initial_luminosity, less_acceptable = True, more_acceptable = True):
        last_frames_luminosity = [initial_luminosity]
        start_time = time.time()
        ok = "NO"
        while time.time() - start_time < self._switching_wait_time:
            data_frame = self.get_frame()
            data_frame_luminosity = numpy.average(data_frame)
    
            while len(last_frames_luminosity) > self._switching_stable_frame_count:
                last_frames_luminosity.pop(0)
    
            #All the frames are withing tolerance
            condition_stable = all(d < data_frame_luminosity * (1 + self._switching_noise_tolerance) and d > data_frame_luminosity * (1 - self._switching_noise_tolerance) for d in last_frames_luminosity)
            condition_not_initial = False
            if initial_luminosity is not None and less_acceptable:
                condition_not_initial = condition_not_initial or data_frame_luminosity < (1 - self._switching_noise_tolerance) * initial_luminosity
            if initial_luminosity is not None and more_acceptable:
                condition_not_initial = condition_not_initial or data_frame_luminosity > (1 + self._switching_noise_tolerance) * initial_luminosity
            
            if condition_stable and condition_not_initial:
                ok = "OK"
                break
    
            last_frames_luminosity.append(data_frame_luminosity)
            
        #print(ok, initial_luminosity, last_frames_luminosity)
        return data_frame
        
    def change_integration_time_and_take_dark_and_data_frames(self, new_integration_time):
        previous_luminosity = numpy.average(self.get_frame())
        
        self._redis_client.publish('hics:camera:shutter_open', 0)
        previous_luminosity = numpy.average(self._switch_wait_luminosity(previous_luminosity, more_acceptable = False))
        
        if getattr(self, "_current_integration_time", None) is None:
            self._redis_client.publish('hics:camera:integration_time', new_integration_time)
            dark_frame = self._switch_wait_luminosity(previous_luminosity)
        else:
            #previous_luminosity = numpy.average(self._switch_wait_luminosity(previous_luminosity, more_acceptable = False))
            
            if numpy.abs(self._current_integration_time - new_integration_time) > self._switching_min_detectable_integration_time_step:
                self._redis_client.publish('hics:camera:integration_time', new_integration_time)
                dark_frame = self._switch_wait_luminosity(previous_luminosity, less_acceptable= new_integration_time < self._current_integration_time, more_acceptable= new_integration_time > self._current_integration_time)
            else:
                if self._current_integration_time < self._max_integration_time / 2:
                    intermediate_integration_time = self._max_integration_time
                else:
                    intermediate_integration_time = self._min_integration_time
                    
                self._redis_client.publish('hics:camera:integration_time', intermediate_integration_time)
                previous_luminosity = numpy.average(self._switch_wait_luminosity(previous_luminosity, less_acceptable= intermediate_integration_time < self._current_integration_time, more_acceptable= intermediate_integration_time > self._current_integration_time))
                
                self._redis_client.publish('hics:camera:integration_time', new_integration_time)
                dark_frame = self._switch_wait_luminosity(previous_luminosity, less_acceptable= new_integration_time < intermediate_integration_time, more_acceptable= new_integration_time > intermediate_integration_time)
                    
            
        dark_frame_luminosity = numpy.average(dark_frame)
        self._current_integration_time = new_integration_time
        
        self._redis_client.publish('hics:camera:shutter_open', 1)
        
        data_frame = self._switch_wait_luminosity(dark_frame_luminosity)
        
        return dark_frame, data_frame
    
    @property
    def min_integration_time_step(self):
        return self._switching_min_detectable_integration_time_step
    
    def move_to(self, target_position, min_speed = None, max_speed = None):
        if min_speed is None:
            min_speed = self._redis_client.get('hics:scanner:velocity_min')
            if min_speed is None:
                min_speed = 10000
            else:
                min_speed = int(min_speed)
                
        if max_speed is None:
            max_speed = self._redis_client.get('hics:scanner:velocity_max')
            if max_speed is None:
                max_speed = 100000
            else:
                max_speed = int(max_speed)
                
        original_speed = int(self._redis_client.get('hics:scanner:velocity'))
                
        tolerance = self._redis_client.get('hics:scanner:scanner_tolerance')
        if tolerance is None:
            tolerance = 0
        else:
            tolerance = int(tolerance)
            
        moving, current_position = self.get_position()
        
        while abs(current_position - target_position) > tolerance or moving:
            max_speed = max(min_speed, min(abs(target_position - current_position), max_speed))
            
            if not moving:
                self._redis_client.publish('hics:scanner:velocity', max_speed)
                self._redis_client.publish('hics:scanner:move_absolute', target_position)
            moving, current_position = self.get_position()
            print(moving, current_position, target_position, max_speed)
            
        self._redis_client.publish('hics:scanner:velocity', original_speed)
        return target_position
    
    def plugin_should_stop(self):
        return not (self._work_thread is not None and self._work_thread.isAlive() )
            
class BaseRecordPlugin(BaseImperativePlugin):
    def _flush_queue(self):
        while not self._queue.empty():
            _dummy = self._queue.get()        
        
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
        
        self._flush_queue()
        idx = 0
        while idx < dark_frames_count:
            frames[:, idx, :] = self.get_frame()[:, 0, :]
            idx += 1
            
        if dark_frame_store_stats:
            storage[prefix+'-avg'] = numpy.average(frames, 1)
            storage[prefix+'-var'] = numpy.var(frames, 1)
            
        end_time = datetime.datetime.now()
        
        return start_time, end_time
        
    
    def _capture_frames(self, storage, prefix, frame_shape, dark_frames_count_before, dark_frames_count_after, data_frames_count = None, capture_end_position = None, reversed_scan = False, dark_frame_store_stats = False, data_frames_skip = 0):
        d0_start_time = None
        d0_end_time = None
        d1_start_time = None
        d1_end_time = None
        data_frame_id = 0
        
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
            
            self._flush_queue()
            
            data_start_time = datetime.datetime.now()
            idx = 0
            while idx < data_frames_count:
                key, data = self._queue.get()
                if key == 'hics:framegrabber:frame_raw':
                    if (data_frame_id % (data_frames_skip + 1)) != 0:
                        data_frame_id += 1
                        continue
                    data_frame_id += 1
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
            
            self._flush_queue()
            frames = []
            moving = False
            while len(frames) == 0 or moving:
                key, data = self._queue.get()
                if key == 'hics:framegrabber:frame_raw' and moving:
                    if (data_frame_id % (data_frames_skip + 1)) != 0:
                        data_frame_id += 1
                        continue
                    data_frame_id += 1
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
