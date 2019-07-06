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

        self.dance_threshold = p["dance_correlation_threshold"]
        self.dance_std_threshold = p["dance_std_threshold"]

        self.frames_per_loop = p["frames_per_loop"] 

        #number of frames to lag/delay for auto correlation
        self.lag = p["frames_per_loop"] 

        self.window_length = p["frames_per_loop"] * 4

        self.frame_buffer = deque(maxlen=self.window_length)

        self.motion_buffer = np.zeros(self.window_length)

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

        #Append the info from this frame to the frame buffer
        self.frame_buffer.append(frame)

        #replace the oldest motion with the latest motion
        self.motion_buffer[0] = motion

        #roll the motion buffer around by 1 step
        self.motion_buffer = np.roll(self.motion_buffer,-1)

        #subtract the mean from the buffer so the signal is zero centered
        X = self.motion_buffer - self.motion_buffer.mean()

        #roll the buffer by the lag amount
        X_lagged = np.roll(X,self.lag)

        #correlate the signal with its lagged version
        correlation = np.sum(X*X_lagged) / max(np.sum(X**2),10e-6)

        #Only return a correlation is the signal amplitude is above a threshold
        if self.motion_buffer.std() > self.dance_std_threshold:
            return correlation
        else:
            return 0.0

    def extract_loop_from_buffer(self):
        """ given dancing has been detected, lets slice out a nice loop from the buffer """

        #Get the mean shifted signal
        X = self.motion_buffer - self.motion_buffer.mean()

        #apply a hamming windo to the signal so the ends taper to zero
        X *= np.hamming(self.window_length)

        #remove the points that are within one loop length of the end. Avoids taking a slice that would go out of range
        X = X[:-self.frames_per_loop]

        #find the index of the smallest motion. This should correspond with the start of a dance move
        smallest_i = int(np.argmin(X))

        #get the start and end index of the loop
        i1 = smallest_i
        i2 = smallest_i+self.frames_per_loop
        
        #slice out the dance loop
        loop_frames = list(self.frame_buffer)[i1:i2]

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
