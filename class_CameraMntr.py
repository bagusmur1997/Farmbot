import threading
import json
import Queue
import random
import math
import time
import Tkinter
import tkMessageBox
import tkFont
import cv2
import numpy as np
from PIL import Image
from PIL import ImageTk
import class_MyThread

from Farmbot_test_excel import *

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

class CameraLink:
    def __init__(self, arg_camera_id):
        self.__camera_idMatrix= [0, 1, 2, 3]
        self.camera_id= arg_camera_id
        self.clean_buffer_judge= True
        self.connect= False
        self.connect_camera(self.camera_id)
        #self.thread_clean_buffer= threading.Thread(target= self.clean_buffer)
        #self.thread_clean_buffer.start()

    def connect_camera(self, arg_camera_id):
        if (self.connect):
            self.cap.release()
            print 'RELEASE...'
        self.camera_id= arg_camera_id
        print '>>> Cam ID ',self.camera_id
        self.cap= cv2.VideoCapture(self.camera_id)
        print 'cap.isOpened:', self.cap.isOpened()
        if not (self.cap.isOpened()):
            for tmp_id in self.__camera_idMatrix:
                try:
                    self.cap= cv2.VideoCapture(tmp_id)
                    print 'Cam ID ',tmp_id,': connected successfully!'
                    self.connect= True
                    self.camera_id= tmp_id
                    Connect_Camera = pd.DataFrame([['2','Connect to Camera', 'Number Channel Camera ":Connected Successfully"', str(tmp_id) + ': Connected Successfully', 'Success']], index=['2'])
                    Connect_Camera.to_excel(writer,'Sheet1', index=False, header=False, startrow=2, startcol= 0)
                    writer.save()
                    break
                except:
                    print 'Cam ID ',tmp_id,': connection Refused!'
                    self.connect= False
                    Connect_Camera = pd.DataFrame([['2', 'Connect to Camera', 'Number Channel Camera ":Connected Successful"', str(tmp_id) + ': Connection Refused', 'Fail']], index=['2'] )
                    Connect_Camera.to_excel(writer,'Sheet1', index=False, header=False, startrow=2, startcol= 0)
                    writer.save()
            if not(self.connect):
                tkMessageBox.showerror("Error","Connection of Camera refused!")
                Connect_Camera = pd.DataFrame([['2', 'Connect to Camera', 'Number Channel Camera ":Connected Successful"', 'Error, Connection of Camera Refused', 'Fail']], index=['2'])
                Connect_Camera.to_excel(writer,'Sheet1', index=False, header=False, startrow=2, startcol= 0)
                writer.save()
        else:
            self.connect= True
            Connect_Camera = pd.DataFrame([['2','Connect to Camera', 'Number Channel Camera ":Connected Successfully"', str(self.camera_id) + ': Connected Successfully', 'Success']], index=['2'])
            Connect_Camera.to_excel(writer,'Sheet1', index=False, header=False, startrow=2, startcol= 0)
            writer.save()

    def get_frame(self):
        if self.cap.isOpened():
            tmp_frame= self.cap.grab()
            _, tmp_frame= self.cap.retrieve()
            return tmp_frame

        else:

            self.connect= False
            #B print 'get_frame() Failed...'
            return -1


    def release_cap(self):
        self.connect= False
        self.cap.release()
        print 'Release Cap()'

    def clean_buffer(self):
        while self.clean_buffer_judge:
            try:
                tmp_frame= self.cap.grab()
            except:
                self.connect= False

    def stop_clean_buffer(self):
        self.clean_buffer_judge= False
    def subract_test(self):
        tmp_frame= self.cap.grab()
        _, tmp_frame= self.cap.retrieve()
        plastic_golden= cv2.imread('Data/Para/background.png')
        test= cv2.subtract(tmp_frame, plastic_golden)
        return test
