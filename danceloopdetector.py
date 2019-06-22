#!/usr/bin/env python3

import cv2
import numpy as np
import math
import queue
from filters import HighPass

class DanceLoopDetector():
    """This class can be called for every frame from a camera and it will return a boolean indicating if someone is dancing"""

    def __init__(self,p):

        self.p = p

        self.lag_queue = queue.Queue()

        self.auto_cor_queue = queue.Queue()

        self.auto_cor_sum = 0.0

        self.last_frame = None

        self.diff_high_pass = HighPass(0.8)

    
    def calc_motion_ratio(self,frame):
        """Calculate the ratio of how much the image has changed since the last image"""

        #convert the frame to int so that it can hold negatives
        frame = frame.astype("int32")

        #initialise the last frame if needed
        if self.last_frame is None: 
            self.last_frame = frame

        #calculate the difference between the last two frames
        diff_frame = np.abs(frame - self.last_frame)

        #sum up the amount of difference
        diff_sum = diff_frame.sum()

        #calculate the maximum difference possible
        h,w,c = frame.shape
        max_sum = h*w*c*255

        #calculate the ratio of the amount of change
        diff_ratio = diff_sum / max_sum

        #is effectively the ratio of the image that contained motion
        return diff_ratio

    def __call__(self,frame):

        #calculate how much motion is in the image
        # 0 = no motion, nothing in the image has changed
        # 1 = full motion, every pixel has changed by full brightness
        motion = self.calc_motion_ratio(frame)

        #Apply high pass filter to get the relative motion as a zero centered signal
        motion = self.diff_high_pass(motion)

        

        #add this motion to the lag queue
        self.lag_queue.put(motion)
        
        #get the 
        return motion




        


if __name__ == "__main__":
    print("hello there")
