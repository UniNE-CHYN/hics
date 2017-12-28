import ev3dev
import select, time
from hics.utils.redis import RedisLink, RedisNotifier

import sys
import math



class EV3Focus:
    def __init__(self):
        self._interface = ev3dev.large_motor()

        self._interface.duty_cycle_sp = 100
        self._interface.stop_command = 'hold'
        
        self._range_from = self.range_min
        self._range_to = self.range_max
        
        time.sleep(1)

    def move_absolute(self, new_position):
        """Move focus to some absolute position"""
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
        moving = int(self._interface.duty_cycle) != 0
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

           

class EV3FocusRedisDaemon(EV3Focus):
    def __init__(self, redis_conn):
        EV3Focus.__init__(self)
        
        self._redis = redis_conn
        self._redis_notifier_state = RedisNotifier(self._redis, 'hics:focus:state', (self, '_redis_focus_state'))
        self._redis_notifier_state.notification_interval = 0.1
        self._redis_link = RedisLink(self._redis, 'hics:focus', self)
        
    def _redis_focus_state(self):
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
        
    focus = EV3FocusRedisDaemon(r)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        focus.stop()
        
