#!/usr/bin/env python3
import cv2

class WebcamInterface():

    def __init__(self):

        self.cap = cv2.VideoCapture(0)

    def read(self):

        ret,frame = self.cap.read()

        return frame