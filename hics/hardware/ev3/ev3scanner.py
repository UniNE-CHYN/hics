import ev3dev
import select, time
from hics.utils.redis import RedisLink, RedisNotifier

import sys
import math



class EV3Scanner:
    def __init__(self):
        self._interface = ev3dev.large_motor()

        self._interface.duty_cycle_sp = 100
        self._interface.stop_command = 'hold'
        
        #10000 around the center is usually more than enough
        self._range_from = -10000
        self._range_to = 10000
        self.velocity_max = 40 * self._factor
        
        time.sleep(1)

    def move_absolute(self, new_position):
        """Move scanner to some absolute position"""
        self._interface.run_to_abs_pos(position_sp = int(new_position))
        
        
        
    def end(self):
        """End current move"""
        self._interface.stop()
        
    @property
    def position(self):
        """Get current position"""
        return self._interface.position
    
    @property
    def moving(self):
        """Return True if the motor is currently moving, False otherwise"""
        duty_cycle = abs(int(self._interface.duty_cycle))
        moving = duty_cycle >= self.velocity_min
        if not moving and duty_cycle != 0:
            self._interface.stop()
        return moving
    
    @property
    def velocity(self):
        """Get maximal velocity"""
        return int(self._interface.duty_cycle_sp)

    @velocity.setter
    def velocity(self, new_velocity):
        """Set maximal velocity"""
        self._interface.duty_cycle_sp = int(new_velocity)
        
    @property
    def velocity_max(self):
        return 100
    
    @property
    def velocity_min(self):
        return 10
    
    @property
    def range_min(self):
        return -4096000
    
    @property
    def range_max(self):
        return 4096000
        
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
    def scanner_limit_slow(self):
        return 20 * self._factor
    
    @scanner_limit_slow.setter
    def scanner_limit_slow(self, newvalue):
        pass  #dummy setter
    @property
    def scanner_limit_fast(self):
        return 100 * self._factor
    @scanner_limit_fast.setter
    def scanner_limit_fast(self, newvalue):
        pass  #dummy setter
    
    @property
    def scanner_tolerance(self):
        return 100 * self._factor
    @scanner_tolerance.setter
    def scanner_tolerance(self, newvalue):
        pass  #dummy setter
           

class EV3ScannerRedisDaemon(EV3Scanner):
    def __init__(self, redis_conn):
        EV3Scanner.__init__(self)
        
        self._redis = redis_conn
        self._redis_notifier_state = RedisNotifier(self._redis, 'hics:scanner:state', (self, '_redis_scanner_state'))
        self._redis_notifier_state.notification_interval = 0.1
        self._redis_link = RedisLink(self._redis, 'hics:scanner', self)
        
    def _redis_scanner_state(self):
        moving, position = self.moving, self.position
        if moving:
            moving = '1'
        else:
            moving = '0'
        return '{0}:{1}'.format(moving, position)
    
    def __del__(self):
        self.stop()
    
    def stop(self, dummy = None):
        self._redis_link.stop()
        self._redis_notifier_state.stop()
        
    @property
    def notification_interval(self):
        return self._redis_notifier_state.notification_interval
    
    @notification_interval.setter
    def notification_interval(self, new_value):
        self._redis_notifier_state.notification_interval = float(new_value)


if __name__ == '__main__':
    import redis, argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", help="Redis URL")
    args = parser.parse_args()
    if args.redis is not None:
        r = redis.from_url(args.redis)
    else:
        r = redis.Redis()
        
    scanner = EV3ScannerRedisDaemon(r)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        scanner.stop()
        
