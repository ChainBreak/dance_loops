#!/usr/bin/env python3

import cv2
import numpy as np
import math
import time
from scipy.signal import fftconvolve
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
        self.window_length = p["window_length_frames"]
        self.cooldown_time = p["dance_detection_cooldown_time"]

        self.frame_buffer = deque(maxlen=self.window_length)

        self.motion_buffer = np.zeros(self.window_length)

        self.last_frame = None

        self.last_detect_time = time.time()
        
        self.plot_dict = {}

    def plot(self,label,value):
        self.plot_dict[label] = self.plot_dict.get(label,[])
        self.plot_dict[label].append(value)
        pass

    def add_frame_to_buffers(self,frame):
        """Calculate the ratio of how much the image has changed since the last image"""

        #Append the info from this frame to the frame buffer
        self.frame_buffer.append(frame)

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

        #replace the oldest motion with the latest motion
        self.motion_buffer[0] = diff_ratio

        #roll the motion buffer around by 1 step
        self.motion_buffer = np.roll(self.motion_buffer,-1)



    def __call__(self,frame):

        if frame is None:
            return
        
        self.add_frame_to_buffers(frame) 

        #subtract the mean from the buffer so the signal is zero centered
        X = self.motion_buffer - self.motion_buffer.mean()

        #apply a windowing function to the signal so the ends taper to zero
        X_windowed = X * np.blackman(self.window_length)

        #calculate the value for correlating the signal with itself for every possible shift
        correlation = np.correlate(X_windowed,X_windowed,"same")

        #the correlation is symetric so just take the second half
        correlation = correlation[len(correlation)//2:]

        #the best correlation is the one with zero shift
        max_correlation = correlation[0]

        #scale the correlations so that the max is now 1.0
        correlation_coeffs = correlation / max_correlation

        #find all the correlations that are less than zero. ie it anti correlates
        negative_correlations = np.where(correlation_coeffs < 0.0)[0]
        
        #if there is at least one negative correlation
        if len(negative_correlations) > 0 and X.std() > self.dance_std_threshold:

            #find the first zero crossing
            zero_crossing_index = negative_correlations[0]

            #find the index of the maximum correlation that comes after the first zero crossing
            #this is the shift that has the best correlation and is the period of the dancing
            best_shift = np.argmax(correlation_coeffs[zero_crossing_index:]) + zero_crossing_index

            best_correlation_ratio = correlation_coeffs[best_shift]
        else:
            best_shift = 0
            best_correlation_ratio = 0.0

        # print(best_correlation_ratio,best_shift)

        
        
        #there is a x second cooldown after every dance is detected
        cooldown_ended = time.time()-self.last_detect_time > self.cooldown_time

        #if dance frequence detected and cooldown ended then trigger a new dance
        if best_correlation_ratio > self.dance_threshold and cooldown_ended:

            #reset cooldown timer
            self.last_detect_time = time.time()

            #add the shifted version to itself
            X_overlayed = X_windowed + np.roll(X_windowed,-best_shift)

            
            start_frame = np.argmin(X_overlayed[:-best_shift])
            end_frame = start_frame + best_shift
            
            loop_frames = list(self.frame_buffer)[start_frame:end_frame]

            #construct a dance loop object to wrap these frames
            dance_loop = DanceLoop(loop_frames)

            self.dance_detection_callback(dance_loop)


        # if best_correlation_ratio > 0.4: 

        #     #add the shifted version to itself
        #     X_overlayed = X_windowed + np.roll(X_windowed,-best_shift)

        #     X_overlayed = X_overlayed[:-best_shift]

        #     start_frame = np.argmin(X_overlayed)
        #     end_frame = start_frame + best_shift

        #     print(start_frame,end_frame)


        #     n = 3
        #     plt.subplot(n,1,1)
        #     plt.plot(X_windowed)
        #     plt.plot(np.roll(X_windowed,best_shift))
        #     plt.plot(X_windowed + np.roll(X_windowed,-best_shift))
        #     plt.subplot(n,1,2)
        #     # plt.plot(np.roll(X_windowed,-best_shift))
        #     plt.plot(X_overlayed)
        #     plt.subplot(n,1,3)
        #     plt.plot(correlation_coeffs)
        #     plt.show()
        #     self.motion_buffer[:] = 0.


