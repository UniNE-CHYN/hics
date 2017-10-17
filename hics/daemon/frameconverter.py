import redis, numpy, pickle, os, inspect, time
import threading

class FrameConverter(threading.Thread):
    def __init__(self, redis_client):
        threading.Thread.__init__(self, name="FrameConverter")
        
        self._continue = True
        self._redis_client = redis_client
        assert isinstance(self._redis_client, redis.client.Redis)
        
        self._shutter_latency = None
        self._max_pixel_value = None
        
        self._shutter_closed_at = None
        self._dark_frames = []
        
    def _reread_variables(self):
        shutter_open = self._redis_client.get('hscc:camera:shutter_open')
        shutter_latency = self._redis_client.get('hscc:camera:shutter_latency')
        max_pixel_value = self._redis_client.get('hscc:camera:max_pixel_value')
        
        if shutter_open is None or shutter_latency is None or max_pixel_value is None:
            return False

        self._shutter_latency = float(shutter_latency)
        self._max_pixel_value = float(max_pixel_value) 
        
        
        if int(shutter_open) == 0 and self._shutter_closed_at is None:
            #If shutter was not closed, and is closed now, it has been closed now
            self._shutter_closed_at = time.time()
        elif int(shutter_open) == 1:
            #Shutter is now open, so clear the closed_at variable
            self._shutter_closed_at = None
            
        return True
        
    def stop(self):
        self._continue = False
        
    def run(self):
        _pubsub = self._redis_client.pubsub()
        _pubsub.subscribe('hscc:framegrabber:frame_raw')
        _pubsub.subscribe('hscc:camera')
        _pubsub.subscribe('hscc:frameconverter')
        
        #Wait until we have valid variables...
        while not self._reread_variables():
            time.sleep(1)
        
        for item in _pubsub.listen():
            #Abort as soon as possible if we intend to stop
            if not self._continue:
                break
            
            if item['type'] not in ('message', 'pmessage'):
                continue
            
            #Decode the channel name
            channel = item['channel']
            if type(channel) == bytes:
                channel = channel.decode('ascii')
                
            #Is this a frame?
            if channel == 'hscc:framegrabber:frame_raw':
                #Load data
                frame = numpy.require(pickle.loads(item['data']), dtype = numpy.float)
                #If shutter is closed and we have enough delay
                if self._shutter_closed_at is not None and time.time() - self._shutter_closed_at > self._shutter_latency:
                    self._dark_frames.append((time.time(), frame))
                    #Remove old dark frames
                    while len(self._dark_frames) > 0 and self._dark_frames[0][0] < time.time() - self._shutter_latency:
                        self._dark_frames.pop(0)
                        
                    print(len(self._dark_frames))
                
                if len(self._dark_frames) > 0:
                    #Use the first dark frame (the others may be not real dark frames, since they are more recent)
                    frame_corrected = frame - self._dark_frames[0][1]
                else:
                    frame_corrected = frame
                
                frame_corrected_clipped = numpy.clip(frame_corrected / self._max_pixel_value, 0, 1)
                
                self._redis_client.publish('hscc:framegrabber:frame', pickle.dumps(frame_corrected_clipped))
            elif channel == 'hscc:camera':
                self._reread_variables()
        
def launch(redis_client, args):
    fc = FrameConverter(redis_client)
    fc.start()
    return fc

def main():
    from hics.utils.daemonize import stdmain
    return stdmain(cb_launch=launch)

if __name__ == '__main__':
    main()
