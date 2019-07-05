#!/usr/bin/env python3
import cv2
import time
import threading

class WebcamInterface():

    def __init__(self):

        self.camera_ready = True



    def connect_to_a_camera(self):
        camera_index = 0

        while True:
            try:
                camera_index = camera_index%10
                print(camera_index)

                self.cap = cv2.VideoCapture(camera_index)
                self.cap.set(cv2.CAP_PROP_FOURCC,cv2.VideoWriter_fourcc('M','J','P','G'))
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25) # .25 manual, .75 auto , Who knows why
                self.cap.set(cv2.CAP_PROP_EXPOSURE, 0.015501550155015502)
                
                ret,frame = self.cap.read()
                
                if frame is not None:
                    self.camera_ready = True
                    return

                camera_index += 1
            except Exception as e:
                print(e)


    def read(self):
        frame = None
        if self.camera_ready:
            try:
                ret,frame = self.cap.read()
            except:
                pass

            if frame is None:
                self.camera_ready = False
                connect_thread = threading.Thread(name="Camera Thread",target=self.connect_to_a_camera,daemon=True)
                connect_thread.start()

        else:
            time.sleep(1/30)

        return frame



        while self.frame is None:
            time.sleep(0.1)
            
        return self.frame
        