
#!/usr/bin/env python3
import cv2
import math
import numpy as np
from collections import deque
from danceloop import DanceLoop


class GridPlayer():

    def __init__(self,frame_size,grid_size):
        #sizes are in width and height

        self.frame_w, self.frame_h = frame_size

        self.grid_w, self.grid_h = grid_size
        self.view_w = self.frame_w // self.grid_w
        self.view_h = self.frame_h // self.grid_h

        self.grid_length = self.grid_w*self.grid_h

        self.frame_count = 0

        self.dance_loop_deque = deque(maxlen=self.grid_length)

        for i in range(self.grid_length):
            self.add_dance_loop(DanceLoop())

    def add_dance_loop(self,dance_loop):
        self.dance_loop_deque.append(dance_loop)

    def get_frame(self):

        frame = np.zeros((self.frame_h,self.frame_w,3),dtype="uint8")

        for i in range(self.grid_h):
            for j in range(self.grid_w):
                i1 = i * self.view_h
                i2 = (i+1) * self.view_h
                j1 = j * self.view_w
                j2 = (j+1) * self.view_w

                li = self.grid_length - (i*self.grid_w + j) -1

                frame[i1:i2,j1:j2,:] = self.dance_loop_deque[li].get_frame( width=self.view_w, height=self.view_h)

        for i in range(self.grid_h):
            y = i * self.view_h
            cv2.line(frame,(0,y), (self.frame_w,y),(0,0,0),10)

        for j in range(self.grid_w):
            x = j * self.view_w
            cv2.line(frame,(x,0), (x,self.frame_h),(0,0,0),10)

        return frame