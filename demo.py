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
    "frames_per_second": 30, #fps of the camera
    "window_length_seconds": 5, #seconds
    "dance_correlation_threshold":0.4, #threshold for when to trigger a new dance
    "pixel_change_threshold":50, #the amount each pixel must change before it is considered to have motion
    "dance_std_threshold":0.0005, 
    "dance_detection_cooldown_time":5, #seconds
    

}
#calculate other tempo parameters
p["window_length_frames"] = round(p["window_length_seconds"] * p["frames_per_second"]) 



camera = Camera()

grid_player = GridPlayer((1920,1080),(6,4))

def dance_detector_callback(new_dance_loop):
    grid_player.add_dance_loop(new_dance_loop)



dance_loop_detector = DanceLoopDetector(dance_detector_callback,p)

cv2.namedWindow("loop",0)
cv2.setWindowProperty('loop', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)


while True:

    frame = camera.read()
    cv2.waitKey(1)
    dance_loop_detector(frame)

   
    if frame is not None:
        cv2.imshow("camera",frame)
        pass
    
    play_frame = grid_player.get_frame()
    
    cv2.imshow("loop",play_frame)
