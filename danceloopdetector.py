#!/usr/bin/env python3

import cv2
import numpy as np
import math
import time
from matplotlib import pyplot as plt
from collections import deque
from filters import HighPass

class DanceLoopDetector():
    """This class can be called for every frame from a camera and it will return a boolean indicating if someone is dancing"""

    def __init__(self,dance_detection_callback,p):

        self.dance_detection_callback = dance_detection_callback
        self.p = p

        self.dance_threshold = p["dance_threshold"]

        self.frames_per_loop = p["frames_per_loop"] 

        #number of frames to lag/delay for auto correlation
        self.lag_length = p["frames_per_loop"] 

        self.lag_buffer = deque()

        self.window_length = p["frames_per_loop"] * 3

        self.window_buffer = deque()

        self.correlation_sum = 0.0

        self.max_correlation_sum = 0.0

        self.last_frame = None

        self.last_detect_time = time.time()
        self.cooldown_time = p["dance_detection_cooldown_time"]

        #TODO calculate high pass value from frame rate and beats per minute
        self.diff_high_pass = HighPass(0.5)

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
        diff_ratio = diff_sum #/ max_sum

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

    def calc_moving_auto_correlation_ratio(self, frame):
        
        #calculate how much motion is in the image
        # 0 = no motion, nothing in the image has changed
        # 1 = full motion, every pixel has changed by full brightness
        motion = self.calc_motion_ratio(frame)

        #Apply high pass filter to get the relative motion as a zero centered signal
        motion = self.diff_high_pass(motion)

        #How much does this frame correlate with a frame 1 period/beat ago
        lagged_product,max_lagged_product = self.calc_lagged_product(motion)

        #Append the info from this frame to the window buffer
        self.window_buffer.append( (frame, motion, lagged_product, max_lagged_product) )

        #add these lagged products to their moving sums
        self.correlation_sum += lagged_product
        self.max_correlation_sum += max_lagged_product

        #if the buffer is not full enough then return 0.0
        if len(self.window_buffer) <= self.window_length:
            return 0.0

        #get the oldest frame info from the buffer
        _, _, oldest_lagged_product, oldest_max_lagged_product = self.window_buffer.popleft()

        #subtract the oldest frame lagged products from the moving sums
        self.correlation_sum -= oldest_lagged_product
        self.max_correlation_sum -= oldest_max_lagged_product

        #calculate the correlation ratio
        self.correlation_ratio = self.correlation_sum / (self.max_correlation_sum + self.window_length*10e-6)

        return self.correlation_ratio

    def extract_loop_from_buffer(self):
        #given dancing has been detected, lets slice out a nice loop from the buffer

        buffer_list = list(self.window_buffer)

        frame_list, motion_list,_,_ = zip(*buffer_list)

        

        smallest_motion = motion_list[0]
        smallest_i = 0

        #find the frame with the smallest motion
        for i,motion in enumerate(motion_list[:-self.frames_per_loop]):
            if motion < smallest_motion:
                smallest_i = i
                smallest_motion = motion

        print(smallest_i,smallest_motion)

        plt.plot(motion_list)
        

        loop_frames = list(frame_list[smallest_i:(smallest_i+int(self.frames_per_loop) )])

        plt.figure()
        for i,frame in enumerate(loop_frames):
            plt.subplot(5,5,i+1)
            plt.imshow(frame)
            plt.title( "frame %i"%i )

        plt.show()

        for i in range(10):
            for frame in loop_frames:
                cv2.imshow("loop",frame)
                cv2.waitKey(int(40))

            loop_frames.reverse()



    def __call__(self,frame):

        #Use auto correlation to see if the dance frequency is in the video
        self.correlation_ratio = self.calc_moving_auto_correlation_ratio(frame)
        
        #there is a x second cooldown after every dance is detected
        cooldown_ended = time.time()-self.last_detect_time > self.cooldown_time

        #if dance frequence detected and cooldown ended then trigger a new dance
        if self.correlation_ratio > self.dance_threshold:
            

            if cooldown_ended:
                print("\n\n\nDance detected")
                self.extract_loop_from_buffer()

            #reset cooldown timer
            self.last_detect_time = time.time()

        return self.correlation_ratio
        
        
        
        
               


if __name__ == "__main__":
    print("hello there")
