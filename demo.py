#!/usr/bin/env python3
import cv2
import math
import numpy as np
import time
from webcam_interface import WebcamInterface as Camera
from danceloopdetector import DanceLoopDetector
from danceloop import DanceLoop
from gridplayer import GridPlayer

p = {
    "beats_per_loop": 2,
    "beats_per_minute": 130,
    "frames_per_second": 30,
    "motion_high_pass":0.95,
    "dance_threshold":0.8,
    "motion_threshold":1.0/100.0, #1 percent
    "dance_detection_cooldown_time":5, #seconds

}
#calculate other tempo parameters
p["frames_per_beat"] = round(p["frames_per_second"] / p["beats_per_minute"] * 60.0) 
p["frames_per_loop"] = round( p["beats_per_loop"] * p["frames_per_second"] / p["beats_per_minute"] * 60.0 )
print(p)

camera = Camera()

grid_player = GridPlayer((1920,1080),(6,4),p["frames_per_loop"])
def dance_detector_callback(new_dance_loop):
    grid_player.add_dance_loop(new_dance_loop)



dance_loop_detector = DanceLoopDetector(dance_detector_callback,p)

# cv2.namedWindow("loop",0)
# cv2.setWindowProperty('loop', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

frame_i = 0

fps = p["frames_per_second"]
frame_time = time.time()
next_frame_time = frame_time + 1./fps
t1=0
while True:
    frame_i += 1
    t1_last = t1
    
    t1 = time.time()
    frame = camera.read()
    t2 = time.time()

    

    dance_loop_detector(frame)

    t3 = time.time()
    
    if frame is not None:
        cv2.imshow("camera",frame)
    play_frame = grid_player.get_frame()
    cv2.imshow("loop",play_frame)

    time_remaining = max(0,next_frame_time - time.time())
    time.sleep(time_remaining)
    next_frame_time = time.time() + 1./fps
    
    cv2.waitKey(1)
    t4 = time.time()

    
    


    print("read",(t2-t1)*1000)
    print("detect",(t3-t2)*1000)
    print("show",(t4-t3)*1000)
    print("loop",(t1-t1_last)*1000)