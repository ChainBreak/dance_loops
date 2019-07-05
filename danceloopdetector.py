#!/usr/bin/env python3

import cv2
import numpy as np
import math
import time
from matplotlib import pyplot as plt
from collections import deque
from danceloop import DanceLoop

class DanceLoopDetector():
    """This class can be called for every frame from a camera and it will return a boolean indicating if someone is dancing"""

    def __init__(self,dance_detection_callback,p):

        self.dance_detection_callback = dance_detection_callback
        self.p = p

        self.dance_threshold = p["dance_threshold"]

        self.frames_per_loop = p["frames_per_loop"] 

        #number of frames to lag/delay for auto correlation
        self.lag = p["frames_per_loop"] 

        self.window_length = p["frames_per_loop"] * 2

        self.window_buffer = deque(maxlen=self.window_length)

        self.auto_cor_buffer = np.zeros(self.window_length)

        self.last_frame = None

        self.last_detect_time = time.time()
        self.cooldown_time = p["dance_detection_cooldown_time"]

        self.plot_dict = {}

    def plot(self,label,value):
        # self.plot_dict[label] = self.plot_dict.get(label,[])
        # self.plot_dict[label].append(value)
        pass

    def calc_motion_ratio(self,frame):
        """Calculate the ratio of how much the image has changed since the last image"""

        #convert the frame to int so that it can hold negatives
        frame = frame.astype("int32")

        #initialise the last frame if needed
        if self.last_frame is None: 
            self.last_frame = frame

        #calculate the difference between the last two frames
        diff_frame = np.abs(frame - self.last_frame)

        self.last_frame = frame

        #sum up the amount of difference
        diff_sum = diff_frame.sum()

        #calculate the maximum difference possible
        h,w,c = frame.shape
        max_sum = h*w*c*255

        #calculate the ratio of the amount of change
        diff_ratio = diff_sum / max_sum

        #is effectively the ratio of the image that contained motion
        return diff_ratio

    def calc_lagged_product(self,motion):
        """An auto correlation is simple a signal multiplied by itself after a delay equal to the period of the frequency you are trying to detect"""

        #add this motion to the lag queue
        self.lag_buffer.append(motion)

        if len(self.lag_buffer) <= self.lag_length:
            return 0.0,0.0

        #get the motion from one period ago
        lagged_motion = self.lag_buffer.popleft()

        #correlate these together
        lagged_product = motion * lagged_motion

        #The best possible correlation they could have
        max_lagged_product = max(motion**2,lagged_motion**2)

        return lagged_product,max_lagged_product

    def calc_auto_correlation(self, frame):
        
        #calculate how much motion is in the image
        # 0 = no motion, nothing in the image has changed
        # 1 = full motion, every pixel has changed by full brightness
        motion = self.calc_motion_ratio(frame)

        # self.plot("motion",motion)

        #Append the info from this frame to the window buffer
        self.window_buffer.append( (frame, motion) )

        #roll the motion buffer around by 1 step
        self.auto_cor_buffer = np.roll(self.auto_cor_buffer,1)

        #replace the oldest motion with the latest motion
        self.auto_cor_buffer[0] = motion

        #subtract the mean from the buffer so the signal is zero centered
        X = self.auto_cor_buffer - self.auto_cor_buffer.mean()

        #roll the buffer by the lag amount
        X_lagged = np.roll(X,self.lag)

        #correlate the signal with its lagged version
        correlation = np.sum(X*X_lagged) / max(np.sum(X**2),10e-6)


        # self.plot("correlation",correlation)
       
        return correlation

    def extract_loop_from_buffer(self):
        #given dancing has been detected, lets slice out a nice loop from the buffer

        #convert the buffer deque to a list
        buffer_list = list(self.window_buffer)

        #convert the list of tuples to a tuple of lists. we only need frames and motions
        frame_list, motion_list = zip(*buffer_list)

        #initialise sum variables to help find the frame with the least motion
        smallest_motion = motion_list[0]
        smallest_i = 0

        #the frame with the smallest motion should be the frame where the dance is at the start of a move
        #find the frame with the smallest motion
        for i,motion in enumerate(motion_list[:-self.frames_per_loop]):

            #if the motion is smaller then update the smallest
            if motion < smallest_motion:
                smallest_i = i
                smallest_motion = motion

        #starting at the frame with the smallest motion, slice out a chuck of video the length of the loop
        i1 = smallest_i
        i2 = smallest_i+self.frames_per_loop
        loop_frames = list(frame_list[i1:i2])

        return loop_frames
        
    def __call__(self,frame):

        if frame is None:
            return
               

        #Use auto correlation to see if the dance frequency is in the video
        self.correlation = self.calc_auto_correlation(frame)
        
        #there is a x second cooldown after every dance is detected
        cooldown_ended = time.time()-self.last_detect_time > self.cooldown_time

        #if dance frequence detected and cooldown ended then trigger a new dance
        if self.correlation > self.dance_threshold and cooldown_ended:
            #reset cooldown timer
            self.last_detect_time = time.time()

            loop_frames = self.extract_loop_from_buffer()

            #construct a dance loop object to wrap these frames
            dance_loop = DanceLoop(loop_frames)

            self.dance_detection_callback(dance_loop)

            # for label,data in self.plot_dict.items():
            #     plt.plot(data,label=label)
            # plt.legend(loc="best")
            # plt.show()


        
        
        
        
               


if __name__ == "__main__":
    print("hello there")
