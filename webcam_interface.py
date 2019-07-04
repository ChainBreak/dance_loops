#!/usr/bin/env python3
import cv2
import time
import threading

class WebcamInterface():

    def __init__(self):

        self.frame = None

        self.camera_thread = threading.Thread(name="Camera Thread",target=self.camera_loop,daemon=True)

        self.lock = threading.Lock()

        self.lock.acquire()

        self.camera_thread.start()

    def camera_loop(self):
        camera_index = 0

        while True:
            try:
                camera_index = camera_index%10
                print(camera_index)

                cap = cv2.VideoCapture(camera_index)
                cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) # .25 manual, .75 auto , Who knows why
                cap.set(cv2.CAP_PROP_EXPOSURE, 0.015501550155015502)

                while True:
                    ret,frame = cap.read()

                    if ret:
                        self.frame = frame
      
                    else:
                        break
                camera_index += 1
            except Exception as e:
                print(e)


    def read(self):
        while self.frame is None:
            time.sleep(0.1)
            
        return self.frame
        