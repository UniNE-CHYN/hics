import serial, threading, os
import select, time
from . import RedisNotifier, RedisLink

import sys
if '/home/fasnachtl/git/thorpy' not in sys.path:
    sys.path.insert(0, '/home/fasnachtl/git/thorpy')
    
import thorpy
import math

class Scanner:
    _factor = 1000 / 360
    _max_velocity = 100
    def __init__(self, port):
        from thorpy.comm.discovery import discover_stages
        stages = list(discover_stages())
        assert len(stages) == 1
        
        self._interface = stages[0]
        time.sleep(1)
        
        self._range_from = -10000
        self._range_to = 10000
        
    def move_absolute(self, new_position):
        """Move scanner to some absolute position"""
        self._interface.position = int(int(new_position) / self._factor)
        
    def end(self):
        """End current move"""
        self._interface.position = self._interface.position
        
    @property
    def position(self):
        """Get current position"""
        return round(self._interface.position * self._factor)
    
    @property
    def moving(self):
        """Return True if the mirror is currently moving, False otherwise"""
        moving = self._interface.velocity != 0.0
        return moving
    
    @property
    def velocity_max(self):
        """Get maximal velocity"""
        return round(self._interface.max_velocity * self._factor)

    @velocity_max.setter
    def velocity_max(self, new_velocity_max):
        """Set maximal velocity"""
        if int(new_velocity_max) >= self._max_velocity:
            self._interface.max_velocity = self._max_velocity / self._factor
        else:
            self._interface.max_velocity = int(new_velocity_max) / self._factor

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
           

class ScannerRedisDaemon(Scanner):
    def __init__(self, redis_conn, port):
        Scanner.__init__(self, port)
        
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
    import redis, argparse, redisrpc
    parser = argparse.ArgumentParser()
    parser.add_argument("--redis", help="Redis URL")
    parser.add_argument("--port", help="Serial port")
    args = parser.parse_args()
    if args.redis is not None:
        r = redis.from_url(args.redis)
    else:
        r = redis.Redis()
        
    scanner = ScannerRedisDaemon(r, args.port)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        scanner.stop()
        
