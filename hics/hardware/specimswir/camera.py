import serial, os
import time
from hics.utils.redis import RedisLink

class CameraInterface:
    def __init__(self, port):
        if port is None:
            port = self._find_port()
        self._serial = serial.Serial(port, baudrate = 9600, timeout = 10)
        
    def flush(self):
        old_timeout = self._serial.timeout
        self._serial.setTimeout(1)
        
        d = None
        while d is None or len(d) != 0:
            d = self._serial.read(1)
        
        self._serial.setTimeout(old_timeout)
        
    def _find_port(self):
        return '/dev/' + [x for x in os.listdir('/sys/bus/usb-serial/drivers/pl2303') if x.startswith('ttyUSB')][0]
        
    def message_read(self):
        d = bytes([])
        #while len(d) == 0 or d[0] != 2:
        #    d = self._serial.read(1)
        d = self._serial.read(1)
        if d == b'':
            return None
        assert d[0] == 2, 'Invalid start byte'
        d = self._serial.read(2)
        assert d[1] == 0, 'reserved-00 invalid'
        length = d[0]
        data = self._serial.read(length)
        d = self._serial.read(2)
        assert (sum(list(data)) % 256) == d[0], 'Invalid checksum'
        assert d[1] == 3, 'Invalid end byte'
        return data.split(b',')
    
    def message_write(self, msg):
        assert type(msg) == list
        for x in msg:
            assert type(x) == bytes
            
        data = b','.join(msg)
        assert len(data) < 256
            
        m = bytes([2, len(data), 0] + list(data) + [sum(list(data)) % 256, 3])
        self._serial.write(m)
        
    def fileno(self):
        return self._serial.fileno()

class Camera:
    def __init__(self, port, debug=False):
        self._debug = debug
        
        super().__init__()
        self._interface = CameraInterface(port)
        self._check_communication()
        
        #Init internal state variables
        self._nuc = None
        self._bad_pixel_replacement = None
        self._frame_rate = None
        self._external_trigger = None
        self._integration_time = None
        self._shutter_open = None
        
        self.shutter_open = True
        self.nuc = 2
        self.bad_pixel_replacement = True
        ret = self._send_message_assert_ok([b'GFR'])
        self.frame_rate = int(ret[2])
        self.external_trigger = False
        self.integration_time = 2600

        #> [b'DAG', b'']
        #< [b'DAG', b'1', b'']
        ##Get remapping
        #> [b'GRM', b'']
        #< [b'GRM', b'1', b'0', b'0', b'1', b'']
        #> [b'ARM', b'']
        #< [b'ARM', b'0', b'']
        ##Get integration time
        #> [b'GIT', b'0', b'']
        #< [b'GIT', b'1', b'2600.0', b'0.0', b'']
        #> [b'GFR', b'']
        #< [b'GFR', b'1', b'50', b'']
        #> [b'DRM', b'']
        #< [b'DRM', b'1', b'']
        #> [b'ANU', b'2', b'']
        #< [b'ANU', b'1', b'']
        #> [b'API', b'2', b'']
        #< [b'API', b'1', b'']
        #> [b'SEX', b'0', b'']
        #< [b'SEX', b'1', b'']
        #> [b'SEX', b'0', b'']
        #< [b'SEX', b'1', b'']
        #> [b'INT', b'1000', b'']
        #< [b'INT', b'1', b'']
        #> [b'GEX', b'']
        #< [b'GEX', b'1', b'0', b'']
        #> [b'FRM', b'50']
        #< [b'FRM', b'1', b'']
        #> [b'INT', b'2600', b'']
        #< [b'INT', b'1', b'']
        #> [b'GIT', b'0', b'']
        #< [b'GIT', b'1', b'2600.0', b'0.0', b'']
        #> [b'GFR', b'']
        #< [b'GFR', b'1', b'50', b'']
        
        
        #?
        self._send_message_assert_ok([b'DAG'])
        
        #Get remapping?
        
        #FIXME: do something to avoid crashing the camera by making too many changes at the same time
        
    def _send_message_assert_ok(self, msg, noassert=False):
        self._interface.message_write(msg)
        ret = self._interface.message_read()
        if self._debug:
            print('>', msg)
            print('<', ret)
        if ret is None:
            return ret
        if not noassert:
            assert ret[0] == msg[0]
            assert ret[1] == b'1'
        return ret
        
    def _check_communication(self):
        self._interface.flush()
        while self._send_message_assert_ok([b'CCM']) is None:
            pass
        
    @property
    def max_pixel_value(self):
        """Maximum pixel value"""
        return 16383
    
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
        
        if new_nuc > 0: 
            #?
            self._send_message_assert_ok([b'DRM'])
            #Activate NUC
            self._send_message_assert_ok([b'ANU', new_nuc_text])
            
            #Reset flip (since we cannot activate flip with nuc, it's better to disable it always)
            ret = self._send_message_assert_ok([b'GRM'])
            while int(ret[4]) != 0:
                if int(ret[4]) & 0x1 == 0x1:
                    self._send_message_assert_ok([b'FIV'])
                if int(ret[4]) & 0x2 == 0x2:
                    self._send_message_assert_ok([b'FIH'])
                ret = self._send_message_assert_ok([b'GRM'])
            
        else:
            #Deactivate NUC
            self._send_message_assert_ok([b'BNU'])
            self._bad_pixel_replacement = False
            
        self._nuc = new_nuc
        self._send_message_assert_ok([b'GNU'])
        
    
        
    @property
    def bad_pixel_replacement(self):
        return self._bad_pixel_replacement
    
    @bad_pixel_replacement.setter
    def bad_pixel_replacement(self, new_bpr):
        new_bpr = self._to_bool(new_bpr)
        if new_bpr:
            assert self._nuc != 0, 'Cannot have BPR and no NUC'
        
        if new_bpr:
            self._send_message_assert_ok([b'API'])
        else:
            self._send_message_assert_ok([b'DPI'])
            
        self._bad_pixel_replacement = new_bpr
        
    @property
    def frame_rate(self):
        return self._frame_rate
    
    @frame_rate.setter
    def frame_rate(self, new_frame_rate):
        new_frame_rate = int(new_frame_rate)
        assert type(new_frame_rate) == int
            
        #assert new_frame_rate <= 20000 and new_frame_rate >= 3
        self._send_message_assert_ok([b'FRM', '{0}'.format(new_frame_rate).encode('ascii')])
        self._frame_rate = new_frame_rate
        
    @property
    def external_trigger(self):
        return self._external_trigger
    
    @external_trigger.setter
    def external_trigger(self, new_external_trigger):
        new_external_trigger = self._to_bool(new_external_trigger)
        if new_external_trigger:
            self._send_message_assert_ok([b'SEX', b'1'])
        else:
            self._send_message_assert_ok([b'SEX', b'0'])
        self._external_trigger = new_external_trigger
        
    def _call_shutter_helper(self, arguments):
        import os, subprocess
        exe_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'helpers', 'specimswir', 'shutter', 'shutter')
        subprocess.call([exe_path] + arguments)
        
    @property
    def shutter_open(self):
        return self._shutter_open
    
    @shutter_open.setter
    def shutter_open(self, new_shutter_open):
        new_shutter_open = self._to_bool(new_shutter_open)
        
        if new_shutter_open:
            self._call_shutter_helper(['1'])
        else:
            self._call_shutter_helper(['0'])
        self._shutter_open = {True: 1, False: 0}[new_shutter_open]
        
    @property
    def integration_time(self):
        return self._integration_time
    
    @integration_time.setter
    def integration_time(self, new_integration_time):
        new_integration_time = float(new_integration_time)
        #assert new_integration_time <= 20000 and new_integration_time >= 1
        self._send_message_assert_ok([b'INT', '{0:0.1f}'.format(new_integration_time).encode('ascii'), b'0', b'0', b'1'])
        self._integration_time = new_integration_time
        
        #Check if the frame rate has changed
        ret = self._send_message_assert_ok([b'GFR'])
        new_frame_rate = int(ret[2])
        if self.frame_rate != new_frame_rate:
            self.frame_rate = new_frame_rate
            self.notify('frame_rate')
            
        
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
        
class CameraRedisDaemon(Camera):
    def __init__(self, redis_conn, port, debug):
        Camera.__init__(self, port, debug)
        
        self._redis = redis_conn
        self._redis_link = RedisLink(self._redis, 'hscc:camera', self)
        
    def __del__(self):
        self.stop()
    
    def stop(self, dummy = None):
        self._redis_link.stop()
        
    def notify(self, prop):
        self._redis_link.notify(prop)

def add_arguments(parser):
    parser.add_argument("--port", help="Camera serial port")
    parser.add_argument("--debug", help="Debug", action="store_true")
    
def launch(redis_client, args):
    return CameraRedisDaemon(redis_client, args.port, args.debug)

def main():
    from hics.utils.daemonize import stdmain
    return stdmain(cb_launch=launch, cb_add_arguments_to_parser=add_arguments)

if __name__ == '__main__':
    main()
