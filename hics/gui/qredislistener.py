from PyQt4 import QtCore
import time
import numpy
import redis
import struct

class RedisListener(QtCore.QThread):
    _channel = 'hics:qtapp:redislistener'
    
    camera_changed = QtCore.pyqtSignal()
    scanner_changed = QtCore.pyqtSignal()
    focus_changed = QtCore.pyqtSignal()
    
    plugin_announce_received = QtCore.pyqtSignal(str)
    plugin_notification_received = QtCore.pyqtSignal(str)
    plugin_output_received = QtCore.pyqtSignal(str, int, bytes)
    plugin_output_after_received = QtCore.pyqtSignal(str, int, bytes)
    
    webcam_picture_received = QtCore.pyqtSignal(numpy.ndarray)
    hypcam_picture_received = QtCore.pyqtSignal(numpy.ndarray)
    
    def __init__(self, redis_client = None, *a, **kw):
        super().__init__(*a, **kw)
        self._stop = False
        
        self._redis = redis_client
        
        self._signals = {}
        
    def run(self):
        pubsub = self._redis.pubsub()
        pubsub.subscribe('hics:webcam:frame')
        pubsub.subscribe('hics:framegrabber:frame')
        pubsub.subscribe(self._channel)
        pubsub.subscribe('hics:scanner')
        pubsub.subscribe('hics:scanner:state')
        pubsub.subscribe('hics:focus:state')
        pubsub.subscribe('hics:camera')
        pubsub.subscribe('hics:plugin:announce')
        pubsub.subscribe('hics:plugin:notification')
        pubsub.psubscribe('hics:plugin:*:output:*')
        pubsub.psubscribe('hics:plugin:*:output_after:*')
        
        for m in pubsub.listen():
            if m['type'] not in ('message', 'pmessage'):
                continue
            
            channel = m['channel']
            if type(channel) == bytes:
                channel = channel.decode('ascii')
                
            data = m['data']
            assert type(data) == bytes
            
            #Stop if we get a message to ourselves
            if channel == self._channel:
                if data == '{0}:STOP'.format(hash(self)).encode('ascii'):
                    break
            
            if m['type'] == 'pmessage' and m['pattern'] in (b'hics:plugin:*:output:*', b'hics:plugin:*:output_after:*'):
                parts = channel.split(':')
                plugin_key = parts[2]
                output_after = (parts[3] == 'output_after')
                output_id = int(parts[4])
                
                if output_after:
                    self.plugin_output_after_received.emit(plugin_key, output_id, data)
                else:
                    self.plugin_output_received.emit(plugin_key, output_id, data)
            
            success = self._map_message_to_signal(channel, data)
            #import cProfile
            #cProfile.runctx("self._map_message_to_signal(channel, data)", locals(), globals())
            
    def _map_message_to_signal(self, channel, data):
        if type(channel) == bytes:
            channel = channel.decode('ascii')
            
        frame_signal_map = {
            'hics:webcam:frame': 'webcam_picture_received',
            'hics:framegrabber:frame': 'hypcam_picture_received',
        }
        changed_signal_map = {
            'hics:camera': 'camera_changed',
            'hics:scanner': 'scanner_changed',
            'hics:scanner:state': 'scanner_changed',
            'hics:focus:state': 'focus_changed',
        }
        value_signal_map = {
            'hics:plugin:announce': 'plugin_announce_received',
            'hics:plugin:notification': 'plugin_notification_received',
        }
        
        if channel in frame_signal_map.keys():
            if self._is_connected(frame_signal_map[channel]):
                getattr(self, frame_signal_map[channel]).emit(numpy.loads(data))
            return True
        elif channel in changed_signal_map.keys():
            getattr(self, changed_signal_map[channel]).emit()
        elif channel in value_signal_map.keys():
            if type(data) == bytes:
                d = data.decode('ascii')
            else:
                d = data
            getattr(self, value_signal_map[channel]).emit(d)
        else:
            return False
        
    def _is_connected(self, signame):
        #This stuff is only to provide a performance improvement, but is bad practice
        #One could replace this by return True, without any functional change
        if signame not in self._signals:
            metaobject = self.metaObject()
            signatures = []
            for i in range(metaobject.methodCount()):
                mosig = metaobject.method(i).signature().split('(', 1)[0]
                if signame == mosig:
                    signatures.append(metaobject.method(i).signature())
                    
            assert len(signatures) > 0
            self._signals[signame] = signatures
            

        num = sum([self.receivers(QtCore.SIGNAL(s)) for s in self._signals[signame]])
        #print(signame, num)
        return num > 0
            
    def stop(self):
        self._redis.publish(self._channel, '{0}:STOP'.format(hash(self)).encode('ascii'))
        self._stop = True
