import numpy
from mmappickle import mmapdict
import threading
import redis
import time
import pickle
import scipy.ndimage

from hics.utils.redis import RedisLink, RedisNotifier

class SimulatorFramegrabber(threading.Thread):
    def __init__(self, simulator):
        threading.Thread.__init__(self, name=self.__class__.__name__)
        self._simulator = simulator
        
    @property
    def _redis(self):
        return self._simulator._redis
    
    @property
    def _data(self):
        return self._simulator._data
    
    def run(self):
        """Run the thread"""
        self._redis.set(
            'hics:framegrabber:wavelengths',
            ','.join('{0:0.02f}'.format(x) for x in self._data['wavelengths'])
        )
        
        self._redis.set(
            'hics:framegrabber:frameheight',
            self._data['scan-00000'].shape[0]
        )
        
        max_measured_pixel = self._simulator.image.max()
        
        #Min power of 2, greater than the max measured value
        self._redis.set(
            'hics:framegrabber:max_pixel_value',
            2**(numpy.ceil(numpy.log(max_measured_pixel+1) / numpy.log(2))) - 1
        )
        
        while self._simulator.running:
            time.sleep(1/self._simulator._camera.frame_rate)
            
            self._redis.publish('hics:framegrabber:frame_raw', pickle.dumps(self._simulator.get_frame()))

        self._redis.delete('hics:framegrabber:wavelengths')
        self._redis.delete('hics:framegrabber:frameheight')
        self._redis.delete('hics:framegrabber:max_pixel_value')
        
        
class SimulatorCamera:
    def __init__(self, simulator):
        self._simulator = simulator
        
        self.shutter_open = True
        self.nuc = 2
        self.bad_pixel_replacement = True
        self.frame_rate = 25
        self.external_trigger = False
        self.integration_time = 2600
        
    @property
    def _redis(self):
        return self._simulator._redis
    
    @property
    def _data(self):
        return self._simulator._data
    
    @property
    def shutter_latency(self):
        """Latency in seconds for the shutter (i.e. the change has been made at redis-time +- shutter_latency"""
        return 1.
        
    @property
    def nuc(self):
        return self._nuc
    
    @nuc.setter
    def nuc(self, new_nuc):
        new_nuc = int(new_nuc)
        if new_nuc not in (0, 1, 2, 3):
            raise ValueError("Invalid NUC {0}".format(new_nuc))
        
        new_nuc_text = '{0}'.format(new_nuc).encode('ascii')
        
        if new_nuc == 0: 
            #Deactivate NUC and bad pixel replacement
            self._bad_pixel_replacement = False
            
        self._nuc = new_nuc        
    
        
    @property
    def bad_pixel_replacement(self):
        return self._bad_pixel_replacement
    
    @bad_pixel_replacement.setter
    def bad_pixel_replacement(self, new_bpr):
        new_bpr = self._to_bool(new_bpr)
        self._bad_pixel_replacement = new_bpr
        
    @property
    def frame_rate(self):
        return self._frame_rate
    
    @frame_rate.setter
    def frame_rate(self, new_frame_rate):
        new_frame_rate = int(new_frame_rate)
        assert type(new_frame_rate) == int
        self._frame_rate = new_frame_rate
        
    @property
    def frame_rate_min(self):
        return 1
    
    @property
    def frame_rate_max(self):
        return 200
        
    @property
    def external_trigger(self):
        return self._external_trigger
    
    @external_trigger.setter
    def external_trigger(self, new_external_trigger):
        new_external_trigger = self._to_bool(new_external_trigger)
        self._external_trigger = new_external_trigger
        
    @property
    def shutter_open(self):
        return self._shutter_open
    
    @shutter_open.setter
    def shutter_open(self, new_shutter_open):
        new_shutter_open = self._to_bool(new_shutter_open)
        self._shutter_open = {True: 1, False: 0}[new_shutter_open]
        
    @property
    def integration_time(self):
        return self._integration_time
    
    @integration_time.setter
    def integration_time(self, new_integration_time):
        new_integration_time = float(new_integration_time)
        self._integration_time = new_integration_time
        
        max_fps = int(1e6 / self._integration_time)
        if self.frame_rate > max_fps:
            self.frame_rate = max_fps
            
    @property
    def integration_time_min(self):
        return 1
    
    @property
    def integration_time_max(self):
        return 20000
            
        
    def _to_bool(self, v):
        if type(v) == bytes:
            return v == b'1'
        elif type(v) == str:
            return v == '1'
        elif type(v) == int:
            return v == 1
        elif type(v) == bool:
            return v
        else:
            raise ValueError("Unknown value type {0!r}".format(v))
    
    def notify(self, prop):
        return
            
            
class SimulatorScanner:
    def __init__(self, simulator):
        self._simulator = simulator
        
        self._range_from = 0
        self._range_to = self._simulator.image.shape[1]
        self._velocity = int((self._range_to - self._range_from) / 20)
        
        self._simulator_position = (self.range_min + self.range_max) // 2
        self._simulator_target = self._simulator_position
        
    def move_absolute(self, new_position):
        self._simulator_target = int(new_position)
        self._simulator_target_velocity = self.velocity
        
    def end(self):
        """End current move"""
        self._simulator_target = self._simulator_position
        
    @property
    def position(self):
        """Get current position"""
        return int(self._simulator_position)
    
    @property
    def moving(self):
        """Return True if the mirror is currently moving, False otherwise"""
        return self._simulator_position != self._simulator_target
    
    @property
    def velocity(self):
        return self._velocity

    @velocity.setter
    def velocity(self, new_velocity):
        self._velocity = int(new_velocity)
        
    @property
    def range_from(self):
        return self._range_from

    @range_from.setter
    def range_from(self, new_value):
        self._range_from = int(new_value)
        
    @property
    def range_to(self):
        return self._range_to

    @range_to.setter
    def range_to(self, new_value):
        self._range_to = int(new_value)
        
    @property
    def velocity_max(self):
        return 400000
    
    @property
    def velocity_min(self):
        return 1
    
    @property
    def range_min(self):
        return -self._simulator.image.shape[1]
    
    @property
    def range_max(self):
        return 2 * self._simulator.image.shape[1]
    
    def _state(self):
        moving, position = self.moving, self.position
        if moving:
            moving = '1'
        else:
            moving = '0'
        return '{0}:{1}'.format(moving, position)
    
    def _update_state(self, dt):
        if self._simulator_target > self._simulator_position:
            delta = min(dt*self._simulator_target_velocity, self._simulator_target-self._simulator_position)
        elif self._simulator_target < self._simulator_position:
            delta = max(-dt*self._simulator_target_velocity, self._simulator_target-self._simulator_position)
        else:
            delta = 0
        
        self._simulator_position += delta
        
        
class SimulatorFocus:
    def __init__(self, simulator):
        self._simulator = simulator
        
        self._range_from = -1000
        self._range_to = 1000
        self._velocity = 200
        
        self._simulator_position = 0
        self._simulator_target = self._simulator_position
        
    def move_absolute(self, new_position):
        self._simulator_target = int(new_position)
        
    def end(self):
        """End current move"""
        self._simulator_target = self._simulator_position
        
    @property
    def position(self):
        """Get current position"""
        return int(self._simulator_position)
    
    @property
    def moving(self):
        """Return True if the mirror is currently moving, False otherwise"""
        return self._simulator_position != self._simulator_target
        
    @property
    def range_from(self):
        return self._range_from

    @range_from.setter
    def range_from(self, new_value):
        self._range_from = int(new_value)
        
    @property
    def range_to(self):
        return self._range_to

    @range_to.setter
    def range_to(self, new_value):
        self._range_to = int(new_value)
        
    @property
    def range_min(self):
        return -1000
    
    @property
    def range_max(self):
        return 1000
    
    def _state(self):
        moving, position = self.moving, self.position
        if moving:
            moving = '1'
        else:
            moving = '0'
        return '{0}:{1}'.format(moving, position)
    
    def _update_state(self, dt):
        if self._simulator_target > self._simulator_position:
            delta = min(dt*self._velocity, self._simulator_target-self._simulator_position)
        elif self._simulator_target < self._simulator_position:
            delta = max(-dt*self._velocity, self._simulator_target-self._simulator_position)
        else:
            delta = 0
        
        self._simulator_position += delta
        
    

class Simulator(threading.Thread):
    def __init__(self, redis_conn, data):
        threading.Thread.__init__(self, name="Simulator")

        self._redis = redis_conn
        assert isinstance(redis_conn, redis.client.Redis)
        self._data = data
        self._continue = True
        
        if 'scan-00000' not in data.keys():
            raise ValueError("Data doesn't contain a scan...")
        
        self._im_integration_time = None
        
        self._camera = SimulatorCamera(self)
        self._scanner = SimulatorScanner(self)
        self._focus = SimulatorFocus(self)
        self._framegrabber = SimulatorFramegrabber(self)
        
        
    def _load_image(self):
        if self._im_integration_time == self._camera.integration_time:
            #nothing to do...
            return
        
        im_keys = list(sorted([k[5:10] for k in self._data.keys() if k[:5] == 'scan-' and k[10:] == '-p']))
        
        im_integration_times = [self._data['scan-{}-p'.format(k)]['integration_time'] for k in im_keys]
        im_ratios = []
        for i in im_integration_times:
            print(i, self._camera.integration_time)
            if i < self._camera.integration_time:
                im_ratios.append(self._camera.integration_time/i)
            else:
                im_ratios.append(i/self._camera.integration_time)
                
        im_id = numpy.argmin(im_ratios)
        ratio = self._camera.integration_time/im_integration_times[im_id]
        imk = im_keys[im_id]
        
        print(imk, ratio, im_ratios)

        
        self._im = self._data['scan-{}'.format(imk)] * ratio
        self._im_d0 = self._data['scan-{}-d0'.format(imk)] * ratio
        self._im_d1 = self._data['scan-{}-d1'.format(imk)] * ratio
        self._im_noise = (self._data['white-{}'.format(imk)] * ratio).std(1)[:, numpy.newaxis, :]
        self._im_integration_time = self._camera.integration_time
        self._im_max_pixel_value = 2**(numpy.ceil(numpy.log(self._im.max()+1) / numpy.log(2))) - 1
        
    @property
    def image(self):
        self._load_image()
        return self._im
    
    def get_frame(self):
        self._load_image()
        im_id = self._scanner.position
        im_width = self.image.shape[1]
        
        if im_id < 0:
            im_data = self.dark_frame_0
        elif im_id >= im_width:
            im_data = self.dark_frame_1
        else:
            pos_p = (im_id / im_width)
            df_at_pos = (1 - pos_p) * self.dark_frame_0 + pos_p * self.dark_frame_0
            
            if self._camera.shutter_open:
                im_data = numpy.random.normal(self.image[:, im_id, numpy.newaxis, :], self._im_noise)
                #Blur the image if needed
                if self._focus.position != 0:
                    im_data = scipy.ndimage.gaussian_filter((im_data - df_at_pos)[:, 0, :], (numpy.abs(self._focus.position/100), 0))[:, numpy.newaxis, :] + df_at_pos
                    
            else:
                im_data = df_at_pos
                
        return numpy.clip(im_data, 0, self._im_max_pixel_value)
    
    @property
    def dark_frame_0(self):
        return numpy.random.normal(self._im_d0, self._im_noise)
        return self._im_d0
    
    @property
    def dark_frame_1(self):
        return numpy.random.normal(self._im_d1, self._im_noise)
        return self._im_d1
        
    def run(self):
        self._framegrabber.start()
        redis_link_camera = RedisLink(self._redis, 'hics:camera', self._camera)
        
        redis_link_scanner = RedisLink(self._redis, 'hics:scanner', self._scanner)
        redis_notifier_scanner = RedisNotifier(self._redis, 'hics:scanner:state', (self._scanner, '_state'))
        redis_notifier_scanner.notification_interval = 0.1
        
        redis_link_focus = RedisLink(self._redis, 'hics:focus', self._focus)
        redis_notifier_focus = RedisNotifier(self._redis, 'hics:focus:state', (self._focus, '_state'))
        redis_notifier_focus.notification_interval = 0.1        
        
        
        ts = time.time()
        while self.running:
            time.sleep(0.01)
            dt = time.time() - ts
            self._scanner._update_state(dt)
            self._focus._update_state(dt)
            ts += dt
            
        redis_link_focus.stop()
        redis_notifier_focus.stop()
        redis_link_camera.stop()
        redis_link_scanner.stop()
        redis_notifier_scanner.stop()
        

    def stop(self):
        """Stop the thread"""
        self._continue = False

    @property
    def running(self):
        return self._continue
    
def add_arguments(parser):
    parser.add_argument("--datafile", help="Data used to simulate the camera", required=True)
    
def launch(redis_client, args):
    data = mmapdict(args.datafile, True)
    sim = Simulator(redis_client, data)
    sim.start()
    return sim

def main():
    from hics.utils.daemonize import stdmain
    return stdmain(cb_launch=launch, cb_add_arguments_to_parser=add_arguments)

if __name__ == '__main__':
    main()
