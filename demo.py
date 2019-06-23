#!/usr/bin/env python3
import cv2
import math
import numpy as np

from webcam_interface import WebcamInterface as Camera
from danceloopdetector import DanceLoopDetector

p = {
    "beats_per_loop": 2,
    "beats_per_minute": 120,
    "frames_per_second": 25,
    "dance_threshold":0.5,
    "dance_detection_cooldown_time":5, #seconds

}
#calculate other tempo parameters
p["frames_per_beat"] = round(p["frames_per_second"] / p["beats_per_minute"] * 60.0) 
p["frames_per_loop"] = round( p["beats_per_loop"] * p["frames_per_second"] / p["beats_per_minute"] * 60.0 )
print(p)

camera = Camera()

def dance_detector_callback():
    pass

dance_loop_detector = DanceLoopDetector(dance_detector_callback,p)


frame_i = 0
while True:
    frame_i += 1
    frame = camera.read()

    correlation_ratio = dance_loop_detector(frame)


    tempo_img = np.zeros((100,400,3),dtype="uint8")
    x = int( math.sin(frame_i/p["frames_per_loop"]*2*math.pi) * 180 + 200 )
    cv2.rectangle(tempo_img,(0,0),(int(400* correlation_ratio),50),(255,0,0),-1)
    cv2.rectangle(tempo_img,(x-10,50),(x+10,100),(255,0,0),-1)
    cv2.imshow("tempo",tempo_img)

    cv2.imshow("camera",frame)
    cv2.waitKey(1)