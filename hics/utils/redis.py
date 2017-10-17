import redis
import traceback
import threading
import time
import weakref
import types
import numpy
import struct

class RedisLink(threading.Thread):
    def __init__(self, redis_client, channel_name, obj):
        threading.Thread.__init__(self, name = "RedisLink/" + channel_name)
        
        self._redis = redis_client
        assert isinstance(self._redis, redis.client.Redis)
        
        self._channel_name = channel_name
        self._service_channel_name = self._channel_name + ':__redis_link'
        self._obj = weakref.proxy(obj)
        self._continue = True
        
        #Initialize methods and properties
        self._redis_methods = []
        for attr_name in dir(obj.__class__):
            attr_value = getattr(obj.__class__, attr_name)
            if callable(attr_value) and not attr_name.startswith('_'):
                #We can call this, it's a method
                #FIXME: check if we have only one argument!
                self._redis_methods.append(attr_name)
                
        self._redis_properties = []
        for attr_name in dir(obj.__class__):
            attr_value = getattr(obj.__class__, attr_name)
            if type(attr_value) == property and not attr_name.startswith('_'):
                if attr_value.fset is not None or True:
                    #This is a real property (we can set it), so return it
                    self._redis_properties.append(attr_name)
                    
        print("Methods:")
        for x in self._redis_methods:
            print('- {0}:{1}'.format(self._channel_name, x))
        print("")
        print("Properties:")
        for x in self._redis_properties:
            print('- {0}:{1}'.format(self._channel_name, x))
        print('')
        
        self.start()
        
    @property
    def redis_properties(self):
        return self._redis_properties
    
    @property
    def redis_methods(self):
        return self._redis_methods
                
        
    def run(self):
        _pubsub = self._redis.pubsub()
        _pubsub.subscribe(self._service_channel_name)
            
        for method in self.redis_methods:
            _pubsub.subscribe('{0}:{1}'.format(self._channel_name, method))
            self._redis.set(self._channel_name + ':' + method, '<method>')
            
        for prop in self.redis_properties:
            _pubsub.subscribe('{0}:{1}'.format(self._channel_name, prop))
            self._redis.set(self._channel_name + ':' + prop, getattr(self._obj, prop))
        
        
        for item in _pubsub.listen():
            #Abort as soon as possible if we intend to stop
            if not self._continue:
                break
            
            if item['type'] not in ('message', 'pmessage'):
                continue
            
            channel = item['channel']
            if type(channel) == bytes:
                channel = channel.decode('ascii')
            
            if channel == self._service_channel_name:
                self._handle_service_message(item['data'])
                #If we stop, it will send another message which will make it break directly
                #There is therefore no need to check afterward if we need to exit the loop
                continue
            
            assert channel.startswith(self._channel_name)
            
            prop = channel[len(self._channel_name) + 1:]
            
            if prop in self.redis_methods:
                try:
                    getattr(self._obj, prop)(item['data'])
                except Exception as e:
                    traceback.print_exc()
                
            elif prop in self.redis_properties:
                try:
                    old_value = getattr(self._obj, prop)
                    setattr(self._obj, prop, item['data'])
                    new_value = getattr(self._obj, prop)
                    
                    if old_value != new_value:
                        self.notify(prop)
                except Exception as e:
                    traceback.print_exc()
                
                self._redis.set(self._channel_name + ':' + prop, getattr(self._obj, prop))
            
        for x in self.redis_methods + self.redis_properties:
            self._redis.delete(self._channel_name + ':' + x)
        
            
    def notify(self, prop):
        self._redis.publish(self._channel_name, prop)
        
    def _handle_service_message(self, data):
        if type(data) == bytes:
            data = data.decode('ascii')
            
        if data == 'kill':
            self.stop()
        else:
            print("Unknown service message: " + data)
        
    def stop(self):
        self._continue = False
        self._redis.publish(self._service_channel_name, b'kill')
    
class RedisNotifier(threading.Thread):
    #Maximum delay for a change (stop the thread or change the notification interval)
    _maximum_change_delay = 0.1
    
    def __init__(self, redis_client, channel_name, function_call):
        threading.Thread.__init__(self, name = "RedisNotifier/" + channel_name)
        
        self._redis = redis_client
        assert isinstance(self._redis, redis.client.Redis)
        
        self._channel_name = channel_name
        if type(function_call) == tuple:
            #(object, method_name)
            assert type(function_call[1]) == str
            self._function_call = (weakref.proxy(function_call[0]), function_call[1])
        else:
            self._function_call = weakref.proxy(function_call)
        self._continue = True
        
        self._notification_interval = 0.
        self._publish_if_constant = True
        
        print("Notification:")
        print('- ' + self._channel_name)
        print('')
        self.start()
        
    def stop(self):
        self._continue = False    
        
    @property
    def notification_interval(self):
        return self._notification_interval
    
    @notification_interval.setter
    def notification_interval(self, new_value):
        assert type(new_value) == float
        self._notification_interval = new_value
        
    @property
    def publish_if_constant(self):
        return self._publish_if_constant
    
    @publish_if_constant.setter
    def publish_if_constant(self, new_value):
        assert type(new_value) == bool
        self._publish_if_constant = new_value

    def run(self):
        old_value = None
        next_notify = time.time()
        while self._continue:
            time.sleep(max(0, min(self._maximum_change_delay, next_notify - time.time())))
                    
            if self._notification_interval == 0.:
                #No notification required, just loop and wait for the next delay
                next_notify = time.time() + self._maximum_change_delay
                
            elif next_notify < time.time():
                #We need to notify
                next_notify = time.time() + self._notification_interval
                if type(self._function_call) == tuple:
                    new_value = getattr(self._function_call[0], self._function_call[1])()
                else:
                    new_value = self._function_call()
                
                if self._publish_if_constant or old_value != new_value:
                    self._redis.publish(self._channel_name, new_value)
                    self._redis.set(self._channel_name, new_value)
                    new_value = old_value
                    
        self._redis.delete(self._channel_name)
