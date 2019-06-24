#!/usr/bin/env python3
import cv2
import math
import numpy as np

from webcam_interface import WebcamInterface as Camera
from danceloopdetector import DanceLoopDetector
from danceloop import DanceLoop
from gridplayer import GridPlayer

p = {
    "beats_per_loop": 2,
    "beats_per_minute": 130,
    "frames_per_second": 30,
    "dance_threshold":0.4,
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

cv2.namedWindow("loop",0)
cv2.setWindowProperty('loop', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

frame_i = 0

while True:
    frame_i += 1
    frame = camera.read()

    dance_loop_detector(frame)


    cv2.imshow("camera",frame)

    play_frame = grid_player.get_frame()

    cv2.imshow("loop",play_frame)


    cv2.waitKey(1)