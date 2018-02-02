#!/usr/bin/python2
#cv2 doesn't work in python (yet?)

#FIXME: improve this!

import numpy
import cv2
import pickle

import redis, argparse
parser = argparse.ArgumentParser()
parser.add_argument("--redis", help="Redis URL")
args = parser.parse_args()
if args.redis is not None:
    r = redis.from_url(args.redis)
else:
    r = redis.Redis()

cap = cv2.VideoCapture(1)
cap.set(3,1920)
cap.set(4,1080)

average_on = 6

frame_count = 0
frame_sum = None
frame_average_old = None
frame_changed_old = False

test_count = 0

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame_float = numpy.array(frame,dtype=numpy.float)
    
    
    if frame_count == 0:
        frame_sum = frame_float.copy()
    else:
        frame_sum += frame_float
        
    frame_count += 1
    if frame_count < average_on:
        continue
        
    frame_average = frame_sum / frame_count / 256
        
    frame_count = 0
    frame_sum = None
    
    frame_changed = False
    #If changed, do processing
    if frame_average_old is not None:
        delta = numpy.linalg.norm(frame_average_old-frame_average)
        #FIXME: use some kind of adaptive threshold
        if delta > 15:
            frame_changed = True
    
    #always send image, even if nothing moved
    if not frame_changed:# and frame_changed_old:
        imdata = cv2.imencode('.jpg',(frame_average*256).astype(numpy.int))[1].tostring()
        r.publish('hics:webcam', imdata)
        
    
    frame_average_old = frame_average
    frame_changed_old = frame_changed
    

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
