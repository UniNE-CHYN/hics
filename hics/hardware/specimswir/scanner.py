import serial, threading, os
import select, time
from hics.utils.redis import RedisLink, RedisNotifier

class ScannerInterface:
    _debug = False
    def __init__(self, port):
        self._lock = threading.Lock()
        if port is None:
            port = self._find_port()
        self._serial = serial.Serial(port, baudrate = 9600, timeout = 1)
        
    def _find_port(self):
        return '/dev/' + sorted((x for x in os.listdir('/sys/bus/usb-serial/drivers/ftdi_sio') if x.startswith('ttyUSB')), reverse = True)[0]
        
    def fileno(self):
        return self._serial.fileno()
    
    def _readline(self, terminator, prompt = None):
        assert type(terminator) == bytes
        assert type(prompt) == bytes or prompt is None
        last_chars = b''
        data = b''
        while last_chars != terminator:
            new_char = self._serial.read(1)
            if len(new_char) != 1:
                return None
            last_chars += new_char
            
            if data + last_chars == prompt:
                return None
            
            while len(last_chars) > len(terminator):
                data += last_chars[:1]
                last_chars = last_chars[1:]

        return data
    
    def _flush(self):
        r = [self._serial]
        while self._serial in r:
            r, w, e = select.select([self._serial], [], [], 0)
            if self._serial in r:
                data = self._serial.read(1)
                if self._debug:
                    print('Flush:', data)
        
    def send_command(self, command, reply = False):
        self._lock.acquire()
        self._serial.write(command + b'\r')
        if reply:
            d = self._readline(b'\r\n')
        else:
            d = None
        self._flush()
        self._lock.release()
        if self._debug:
            print ('>', command)
            print ('<', d)
        return d
    
class Scanner:
    def __init__(self, port):
        self._interface = ScannerInterface(port)
        #Disable echo
        self._interface.send_command(b'EM=2')
        time.sleep(1)
        #Flush garbage
        self._interface._flush()
        
        self._range_from = 0
        self._range_to = 4096000
        
    def move_absolute(self, new_position):
        """Move scanner to some absolute position"""
        self._interface.send_command('MA {0}'.format(int(new_position)).encode('ascii'))
        
    def end(self):
        """End current move"""
        self._interface.send_command(b'E')
        
    @property
    def position(self):
        """Get current position"""
        position = int(self._interface.send_command(b'PR P', True).decode('ascii'))
        
        return position
    
    @property
    def moving(self):
        """Return True if the mirror is currently moving, False otherwise"""
        moving = self._interface.send_command(b'PR MV', True) == b'1'
        return moving
    
    @property
    def velocity_max(self):
        """Get maximal velocity"""
        return int(self._interface.send_command(b'PR VM', True).decode('ascii'))

    @velocity_max.setter
    def velocity_max(self, new_velocity_max):
        """Set maximal velocity"""
        self._interface.send_command('VM {0}'.format(int(new_velocity_max)).encode('ascii'))
        
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


def add_arguments(parser):
    parser.add_argument("--port", help="Scanner serial port")
    
def launch(redis_client, args):
    return ScannerRedisDaemon(redis_client, args.port)

def main():
    from hics.utils.daemonize import stdmain
    return stdmain(cb_launch=launch, cb_add_arguments_to_parser=add_arguments)

if __name__ == '__main__':
    main()
