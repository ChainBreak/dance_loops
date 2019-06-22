#!/usr/bin/env python3
import cv2
from webcam_interface import WebcamInterface as Camera
from danceloopdetector import DanceLoopDetector

p = {
    "beats_per_loop": 2,
    "beats_per_minute": 120,
    "frames_per_second": 30,

}
#calculate other tempo parameters
# p["frame_per_beat"]
p["frames_per_loop"] = round( p["beats_per_loop"] / (p["beats_per_minute"] / 60.0) * p["frames_per_second"] )


camera = Camera()
dance_loop_detector = DanceLoopDetector(p)

while True:
    frame = camera.read()

    dance_loop_detector(frame)

    cv2.imshow("camera",frame)
    cv2.waitKey(1)