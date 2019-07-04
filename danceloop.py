#!/usr/bin/env python3
import cv2
import math
import numpy as np

#generate a global placeholder sequence for all the danceloops for if they are initialised without a frame list
placeholder_frame_list = []
w=320
h=240
l=50
for i in range(l):
    frame = np.ones((h,w,3),dtype="uint8")*128
    x = int(w/2 - w/3*math.cos(i/l*math.pi*2))
    cv2.line(frame,(x,0),(w//2,h//2),(50,50,50),20)
    # cv2.line(frame,(x,h),(w//2,h//2),(50,50,50),20)
    
    placeholder_frame_list.append(frame)



class DanceLoop():

    def __init__(self,frame_list=placeholder_frame_list):
        #take a local refernce of the frame list
        self.frame_list = frame_list

        #get the length of the frame list
        self.length = len(self.frame_list)

        #create a new empty list of the same size to hold the resized list
        self.resized_frame_list = self.frame_list.copy()
    

    def get_frame(self,ratio,height,width):
        #frames are requested as a ratio of the whole sequence length.
        #This way sequences of different lengths can be played together in synk

        #calculate the frame index from the ratio
        frame_i = int(ratio * self.length)

        #get the frame for this ratio
        frame = self.resized_frame_list[frame_i]

        #check if the frame has the correct shape. Reshape it if it doesn't
        if frame.shape != (height,width,3):
            #crop the frame so that it has the correct aspect ratio
            #Get the aspect ratio of the target size
            aspect = width/height

            h,w,c = frame.shape
            #Calculate the new crop size so that it has the same aspect ratio
            crop_w = int(min(h*aspect,w))
            crop_h = int(min(w/aspect,h))

            #crate the slice indexes for the crp
            w1 = (w - crop_w) // 2
            w2 = w1 + crop_w
            h1 = (h - crop_h) // 2
            h2 = h + crop_h

            #crop out a section with the correct aspect ratio
            cropped_frame = frame[h1:h2,w1:w2,:] 

            #resize the frame so that it is the correct size
            self.resized_frame_list[frame_i] = frame = cv2.resize(cropped_frame,(width,height))

        return frame


if __name__ == "__main__":
    dl = DanceLoop()