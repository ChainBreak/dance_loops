#!/usr/bin/env python3
import cv2

class WebcamInterface():

    def __init__(self):

        self.cap = cv2.VideoCapture(2)
        self.cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    def read(self):

        ret,frame = self.cap.read()

        return frame