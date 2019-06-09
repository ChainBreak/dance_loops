#!/usr/bin/env python3


import cv2
import numpy as np
import queue
from matplotlib import pyplot as plt

if __name__ == "__main__":
    
    
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("cam",0)
    cv2.namedWindow("diff",0)

    last_frame = None

    plot_dict = {}

    def plot(label,value):
        plot_dict[label] = plot_dict.get(label,[])
        plot_dict[label].append(value)

    
    delay_queue = queue.Queue()
    period = 15
    for i in range(period):
        delay_queue.put(0.0)

    autocorrelation_smooth = 0.05

    sum_window_size = 90
    auto_cor_array = np.zeros(sum_window_size)
    max_auto_cor_array = np.zeros(sum_window_size)


    smooth_auto_cor = 0.
    smooth_max_auto_cor = 0.
    smooth_cor_ratio = 0.

    diff_highpass = 0.0
    diff_ratio_last = None

    for frame_i in range(600):
        ret,frame_raw = cam.read()
        
        frame = cv2.cvtColor(frame_raw,cv2.COLOR_BGR2GRAY)
        frame = cv2.resize(frame,(0,0),fx=0.5,fy=0.5).astype("int32")

        cv2.ellipse(frame_raw,(100,100),(50,10),frame_i/period*360,30,-30,(255,0,0))
        cv2.imshow("cam",frame_raw)

        if last_frame is not None:
            diff = np.abs(frame - last_frame).astype("uint8")
            cv2.imshow("diff",diff)

            h,w = diff.shape
            diff_sum = float(diff.sum())
            diff_ratio = diff_sum / h/w/255.0

            #highpass filter the diff_ration
            if diff_ratio_last is None: diff_ratio_last = diff_ratio
            diff_highpass = 0.9 * ( diff_highpass + diff_ratio - diff_ratio_last )


            delay_queue.put(diff_highpass)

            delayed_diff = delay_queue.get()
            autocorrelation = diff_highpass * delayed_diff

            auto_cor_array = np.roll(auto_cor_array,1)
            auto_cor_array[0] = autocorrelation

            max_auto_cor_array = np.roll(max_auto_cor_array,1)
            max_auto_cor_array[0] = max(delayed_diff**2 , diff_highpass**2)

            auto_cor_sum = auto_cor_array.sum()
            max_auto_cor_sum = max_auto_cor_array.sum()
            
            # plot("auto_cor_sum",auto_cor_sum)
            # plot("max_auto_cor_sum",max_auto_cor_sum)

            correlation_ratio = auto_cor_sum/(max_auto_cor_sum+10e-6)
            plot("correlation_ratio",correlation_ratio)

            # # plot("autocorrelation",autocorrelation)
            # smooth_auto_cor += autocorrelation_smooth * (autocorrelation - smooth_auto_cor)
            # # plot("smooth_auto_cor",smooth_auto_cor)

            # max_autocorrelation = delayed_diff **2
            # # plot("max_autocorrelation",max_autocorrelation)
            # smooth_max_auto_cor += autocorrelation_smooth * (max_autocorrelation - smooth_max_auto_cor)

            # # plot("smooth_max_auto_cor",smooth_max_auto_cor)

            # correlation_ratio = autocorrelation/(max_autocorrelation+10e-5)
            # plot("correlation_ratio",correlation_ratio)

            # smooth_cor_ratio += autocorrelation_smooth * ( correlation_ratio - smooth_cor_ratio)
            # plot("smooth_cor_ratio",smooth_cor_ratio)

            # diff_ratio_last = diff_ratio
            # # plot("diff_highpass",diff_highpass)
            # # plot("delayed_diff",delayed_diff)
            

        last_frame = frame
        
        
        
        cv2.waitKey(1)

    for label,data in plot_dict.items():
        plt.plot(data,label=label)
    plt.legend(loc="best")
    plt.show()