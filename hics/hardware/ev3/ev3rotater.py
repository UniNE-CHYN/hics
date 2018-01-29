
import ev3dev
import select, time
from hics.utils.redis import RedisLink, RedisNotifier

import sys
import math

class EV3Rotater:
    _factor = 1
    def __init__(self):
        self._interface = ev3dev.medium_motor()
        time.sleep(1)
        
        self._start_position = self._interface.position
        self._c = 0
        
    def move_next(self):
        """Move to the next position"""
        self._c += 10
        m.run_to_abs_pos(position_sp=self._start_position+self._c*40,speed_sp=360,speed_regulation_enabled='on')
        
    @property
    def position(self):
        """Get current position"""
        return int((self._interface.position - self._start_position) / 40)
    
    @property
    def moving(self):
        """Return True if the mirror is currently moving, False otherwise"""
        moving = int(self._interface.duty_cycle) != 0
        return moving


class EV3RotaterRedisDaemon(EV3Scanner):
    def __init__(self, redis_conn):
        EV3Scanner.__init__(self)
        
        self._redis = redis_conn
        self._redis_notifier_state = RedisNotifier(self._redis, 'hics:rotater:state', (self, '_redis_rotater_state'))
        self._redis_notifier_state.notification_interval = 0.1
        self._redis_link = RedisLink(self._redis, 'hics:rotater', self)
        
    def _redis_rotater_state(self):
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
    import redis, argparse, redisrpc
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", help="Redis URL")
    args = parser.parse_args()
    if args.redis is not None:
        r = redis.from_url(args.redis)
    else:
        r = redis.Redis()
        
    rotater = EV3RotaterRedisDaemon(r)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        rotater.stop()
        
