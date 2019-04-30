import os
import threading
import schedule
import time
from schedule import *
from schedulee import *
from class_PlantIdentifier import PlantIdentifier
import datetime
import sqlite3
import cv2
import numpy as np
import threading
import json
import random
import math
import time
import types
from GUI import PlantDetectionGUI
from PlantDetection import PlantDetection


from tkcalendar import Calendar, DateEntry

import Tkinter as ttk
from ttk import *

import Tkinter
from Tkinter import *
import tkFileDialog
import ttk
import tkMessageBox
import tkFont

import ScrolledText
import Pmw

from PIL import Image
from PIL import ImageTk
from os import listdir, path, makedirs, remove
#from datetime import datetime

from class_ArduinoSerMntr import *
from class_CameraMntr import *
import class_MyThread

import imgProcess_tool
import gui_vars

from class_ConfigSetting import ConfigSetting
#from class_ConfigSetting_new import ConfigSetting

from dialog_PeripheralSetting import PeripheralSetting
from dialog_MotorSetting import MotorSetting
from dialog_CameraConnection import CameraConnection
import utils_tool

import os
import json
import cv2

# Excel
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import numpy as np

from Farmbot_test_excel import *

class App:
    # Ininitalization

    def __init__(self, root):


        # Type of Fontz
        tes = 0
        strFont = 'Arial'
        myfont8 = tkFont.Font(family=strFont, size=8)
        myfont8_Bold = tkFont.Font(family=strFont, size=8, weight= tkFont.BOLD)
        myfont10 = tkFont.Font(family=strFont, size=10)
        myfont10_Bold = tkFont.Font(family=strFont, size=10, weight= tkFont.BOLD)
        myfont12 = tkFont.Font(family=strFont, size=12)
        myfont12_Bold = tkFont.Font(family=strFont, size=12, weight= tkFont.BOLD)
        myfont14 = tkFont.Font(family=strFont, size=14)
        myfont14_Bold = tkFont.Font(family=strFont, size=14, weight= tkFont.BOLD)
        myfont16 = tkFont.Font(family=strFont, size=16)
        myfont16_Bold = tkFont.Font(family=strFont, size=16, weight= tkFont.BOLD)
        myfont18 = tkFont.Font(family=strFont, size=18)
        myfont18_Bold = tkFont.Font(family=strFont, size=18, weight=tkFont.BOLD)

        # List Color Font
        self.bgGreen= '#007700'
        self.bgGreen_active= '#00aa00'

        darkgray='#A9A9A9'
        silver='#C0C0C0'
        bgGray= '#333333333'
        bgGray_active= 'gray'
        bgGray_select= '#999'
        self.bgRed= '#aa0000'
        self.bgRed_active= '#ee0000'
        self.Move_intervalUnit= 1
        self.root= root
        self.root.update()

        # =================================
        # Parameters
        # =================================
        if utils_tool.check_path(gui_vars.saveParaPath):
            print 'ICON...'
            self.img_icon = Tkinter.PhotoImage(file = gui_vars.saveParaPath+'logo_farmbot.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, self.img_icon)

        self.config= ConfigSetting(gui_vars.saveParaPath, gui_vars.configName, gui_vars.defaultDict)
        params= self.config.read_json()
        self.threshold_graylevel= params['thrshd_gray']
        self.threshold_MinSize= params['thrshd_Minsize']
        self.threshold_MaxSize= params['thrshd_Maxsize']
        self.scan_X= params['Scan_X (Beg,Interval,Amount)']
        self.scan_Y= params['Scan_Y (Beg,Interval,Amount)']
        self.limit= params['limit Maximum (X,Y)']
        self.MaxSpeed= params['Max Speed (X, Y)']
        self.Acceleration= params['Ac/Deceleration (X, Y)']
        self.CameraID= params['Camera ID']
        self.Peripheral_para= params['Peripheral Setting']
        self.rdbtnMvAmount_Mode= params['Move Amount type (5 types)']
        self.scriptPath= params['script Path']

        self.pinNumb_fan = 8
        self.pinNumb_water = 9
        self.pinNumb_seed = 10
        self.num_schedule = 0

        self.get_X_pos = 0
        self.get_Y_Pos = 0
        self.get_amount_water = 50

        #for key, value in params['Peripheral Setting']:
        for key, value in self.Peripheral_para:		#2018.02.28
            print key, value	#2018.02.28
            if key.strip().replace(' ','').lower() == 'waterpump':	# is -> == 2018.02.28
                self.pinNumb_water= value
                print 'pinNumb_water: ', self.pinNumb_water		#2018.02.28
            if key.strip().replace(' ','').lower() == 'vaccumpump':	# is -> == 2018.02.28
                self.pinNumb_seed= value
                print 'pinNumb_seed: ', self.pinNumb_seed		#2018.02.28
            if key.strip().replace(' ','').lower() == 'fan':		# is -> == 2018.02.28
		self.pinNumb_fan= value
		print 'pinNumb_fan: ', self.pinNumb_fan			#2018.02.28

        print 'Pin Value: ',self.Peripheral_para	#2018.02.28

        self.checkmouse_panel_mergeframe= False
        self.x1, self.y1, self.x2, self.y2= -1,-1,-1,-1
        self.StartScan_judge= False
        self.StartRunScript_judge= False
        self.saveScanning= 'XXX'
        self.strStatus= 'Idling...'
        self.readmergeframeIndex= ''
        self.Start_Watering_judge= False


        self.root.update()



        self.screen_width, self.screen_height= self.root.winfo_width(), self.root.winfo_height()
        print 'screen: ',[self.root.winfo_screenwidth(), self.root.winfo_screenheight()]
        print 'w, h: ',[self.root.winfo_width(), self.root.winfo_height()]
        btn_width, btn_height= 8, 1
        #gui_vars.interval_x, gui_vars.interval_y= 6, 6
        self.mergeframe_spaceY= 50
        #print width,',', height,' ; ',btn_width,',', btn_height


        # =======================================
        # [Config] Menu Bar
        # =======================================
        self.menubar= Tkinter.Menu(self.root)
        self.FileMenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="File",underline=0, menu=self.FileMenu)
        self.FileMenu.add_command(label="Load Image", command=self.btn_loadImg_click)
        self.FileMenu.add_command(label="Save Image", command=self.btn_saveImg_click)
        self.SettingMenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Setting", underline=0, menu=self.SettingMenu)
        self.SettingMenu.add_command(label= "Peripheral Setting", command= self.set_Peripheral)
        self.SettingMenu.add_command(label= "Motor Setting", command= self.set_Motor)
        self.ConnectMenu = Tkinter.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label="Communication", underline= 0, menu=self.ConnectMenu)
        self.ConnectMenu.add_command(label="Connect to Arduino", command=self.set_ArdConnect)
        self.ConnectMenu.add_command(label="Connect to Camera", command=self.set_CamConnect)



        self.root.config(menu= self.menubar)
        self.root.update()


        # =======================================
        # [Config] Status Bar
        # =======================================
        self.statuslabel = Tkinter.Label(self.root, bd = 1, relief = Tkinter.SUNKEN, anchor = "w")
        self.statuslabel.config(text="IDLING ..................")
        self.statuslabel.pack(side = Tkinter.BOTTOM,fill=Tkinter.X)
        self.root.update()

        # ==================================================
        # [ROOT] Current position of motor
        # ==================================================
        self.lbl_CurrPos= Tkinter.Label(self.root, text="Location: (X, Y, Z)= (0, 0, 0)",font= myfont14_Bold)
        self.lbl_CurrPos.place(x= gui_vars.interval_x, y= gui_vars.interval_y)
        self.root.update()


        # ====================
        # [Config] Tabpages
        # ====================
        self.screen_width, self.screen_height= self.root.winfo_width(), self.root.winfo_height()
        #Left_width= self.lbl_MoveCoord.winfo_reqwidth()+ gui_vars.interval_x*11
        Left_width= int((self.screen_width-gui_vars.interval_x*2)*0.25)
        Left_height= int((self.screen_height-self.FileMenu.winfo_reqheight()*1- self.statuslabel.winfo_reqheight()*0-gui_vars.interval_y*2- self.lbl_CurrPos.winfo_reqheight()))
        self.tabbox = ttk.Notebook(self.root, width=Left_width, height=Left_height)
        self.tab_control = Tkinter.Frame(self.root)
        self.tab_loadscript = Tkinter.Frame(self.root)
        self.tab_event_schedule = Tkinter.Frame(self.root)
        self.tab_planting = Tkinter.Frame(self.root)
        self.tabbox.add(self.tab_control, text="CONTROL")
        self.tabbox.add(self.tab_loadscript, text="SCRIPT")
        self.tabbox.add(self.tab_event_schedule, text="SCHEDULE")
        self.tabbox.add(self.tab_planting, text="PLANT & IMAGE")

	   #self.tabbox.place(x= 0, y= 0)
        self.tabbox.place(x= 0, y= self.lbl_CurrPos.winfo_y()+ self.lbl_CurrPos.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()
        print '*** Input Tab', Left_width, Left_height
        print '*** TAB',self.tabbox.winfo_reqwidth(), self.tabbox.winfo_reqheight()

        # ==================================================
        # [TAB CONTROL] Step Motor Control
        # ==================================================
        self.lbl_MoveCoord= Tkinter.Label(self.tab_control, text="MOVE AMOUNT (MM)".center(38), font= myfont14_Bold)
        self.lbl_MoveCoord.place(x= gui_vars.interval_x, y= gui_vars.interval_y)
        self.root.update()

        # ==================================================
        #  [TAB CONTROL] Move Amount Radio Button
        # ==================================================

        self.MvAmount= Tkinter.IntVar()
        #Move Amount 10 mm
        self.rdbtn_MvAmount_1= Tkinter.Radiobutton(self.tab_control, text= self.rdbtnMvAmount_Mode[0][0], value= self.rdbtnMvAmount_Mode[0][1],variable= self.MvAmount,font= myfont12_Bold, command= self.rdbtn_MvAmount_click, indicatoron=0, width=5, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active,selectcolor= bgGray_select)
        self.rdbtn_MvAmount_1.place(x= gui_vars.interval_x * 3, y=self.lbl_MoveCoord.winfo_y() + self.lbl_MoveCoord.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()

        #Move Amount 50 mm
        self.rdbtn_MvAmount_5= Tkinter.Radiobutton(self.tab_control, text= self.rdbtnMvAmount_Mode[1][0], value=self.rdbtnMvAmount_Mode[1][1], variable= self.MvAmount,font= myfont12_Bold, command= self.rdbtn_MvAmount_click, indicatoron=0, width=5, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active,selectcolor= bgGray_select)
        self.rdbtn_MvAmount_5.place(x= gui_vars.interval_x + self.rdbtn_MvAmount_1.winfo_x() + self.rdbtn_MvAmount_1.winfo_reqwidth(),y= self.rdbtn_MvAmount_1.winfo_y())
        self.root.update()

        #Move Amount 100 mm
        self.rdbtn_MvAmount_10= Tkinter.Radiobutton(self.tab_control, text= self.rdbtnMvAmount_Mode[2][0], value=self.rdbtnMvAmount_Mode[2][1], variable= self.MvAmount,font= myfont12_Bold, command= self.rdbtn_MvAmount_click, indicatoron=0, width=5, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active,selectcolor= bgGray_select)
        self.rdbtn_MvAmount_10.place(x= gui_vars.interval_x + self.rdbtn_MvAmount_5.winfo_x() + self.rdbtn_MvAmount_5.winfo_reqwidth(),y= self.rdbtn_MvAmount_1.winfo_y())
        self.root.update()

        #Move Amount 200 mm
        self.rdbtn_MvAmount_20= Tkinter.Radiobutton(self.tab_control, text= self.rdbtnMvAmount_Mode[3][0], value=self.rdbtnMvAmount_Mode[3][1], variable= self.MvAmount,font= myfont12_Bold, command= self.rdbtn_MvAmount_click, indicatoron=0, width=5, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active,selectcolor= bgGray_select)
        self.rdbtn_MvAmount_20.place(x= gui_vars.interval_x + self.rdbtn_MvAmount_10.winfo_x() + self.rdbtn_MvAmount_10.winfo_reqwidth(),y= self.rdbtn_MvAmount_1.winfo_y())
        self.root.update()

        #Move Amount 500 mm
        self.rdbtn_MvAmount_50= Tkinter.Radiobutton(self.tab_control, text= self.rdbtnMvAmount_Mode[4][0], value=self.rdbtnMvAmount_Mode[4][1], variable= self.MvAmount,font= myfont12_Bold, command= self.rdbtn_MvAmount_click, indicatoron=0, width=5, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active,selectcolor= bgGray_select)
        self.rdbtn_MvAmount_50.place(x= gui_vars.interval_x + self.rdbtn_MvAmount_20.winfo_x() + self.rdbtn_MvAmount_20.winfo_reqwidth(),y= self.rdbtn_MvAmount_1.winfo_y())
        self.root.update()


        self.rdbtn_MvAmount_1.select()  					#2018.02.28
        self.Move_interval= self.rdbtnMvAmount_Mode[0][1]   #2018.02.28

        self.lbl_posUnit_1= Tkinter.Label(self.tab_control, text='')
        self.lbl_posUnit_1.place(x= self.rdbtn_MvAmount_50.winfo_x() + self.rdbtn_MvAmount_50.winfo_width(), y= self.rdbtn_MvAmount_1.winfo_y()+gui_vars.interval_y)
        self.root.update()

        # ==================================================
        # [TAB CONTROL] Move 1 interval at specific Axis
        # ==================================================

        # Move Axis X
        photo_up= self.IconResize(gui_vars.saveParaPath+'img_Up.png')
        self.btn_MoveUp= Tkinter.Button(self.tab_control,image= photo_up, cursor= 'hand2', command= lambda: self.btn_MoveAmount_click('Up'))
        self.btn_MoveUp.image= photo_up
        self.btn_MoveUp.place(x= self.rdbtn_MvAmount_10.winfo_x()+int(self.rdbtn_MvAmount_10.winfo_reqwidth()*0), y=self.rdbtn_MvAmount_1.winfo_y()+ self.rdbtn_MvAmount_1.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()

        # Move Axis X Invert
        photo_down= self.IconResize(gui_vars.saveParaPath+'img_Down.png')
        self.btn_MoveDown= Tkinter.Button(self.tab_control,image= photo_down, cursor= 'hand2', command= lambda: self.btn_MoveAmount_click('Down'))
        self.btn_MoveDown.image= photo_down
        self.btn_MoveDown.place(x= self.btn_MoveUp.winfo_x(), y=self.btn_MoveUp.winfo_y()+ self.btn_MoveUp.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()

        # Move Axis Y
        photo_left= self.IconResize(gui_vars.saveParaPath+'img_Left.png')
        self.btn_MoveLeft= Tkinter.Button(self.tab_control,image= photo_left, cursor= 'hand2', command= lambda: self.btn_MoveAmount_click('Left'))
        self.btn_MoveLeft.image= photo_left
        self.btn_MoveLeft.place(x= self.btn_MoveDown.winfo_x()- self.btn_MoveDown.winfo_width()- gui_vars.interval_x, y=self.btn_MoveDown.winfo_y())
        self.root.update()

        # Move Axis Y Invert
        photo_right= self.IconResize(gui_vars.saveParaPath+'img_Right.png')
        self.btn_MoveRight= Tkinter.Button(self.tab_control,image= photo_right, cursor= 'hand2', command= lambda: self.btn_MoveAmount_click('Right'))
        self.btn_MoveRight.image= photo_right
        self.btn_MoveRight.place(x= self.btn_MoveDown.winfo_x()+ self.btn_MoveDown.winfo_width()+ gui_vars.interval_x, y=self.btn_MoveDown.winfo_y())
        self.root.update()

        # Move Axis Z
        self.btn_MoveZUp= Tkinter.Button(self.tab_control,image= photo_up, cursor= 'hand2', command= lambda: self.btn_MoveAmountZaxis_click('Up'))
        self.btn_MoveZUp.image= photo_up
        self.btn_MoveZUp.place(x= self.btn_MoveRight.winfo_x()+ self.btn_MoveRight.winfo_reqwidth()+ gui_vars.interval_x*4, y=self.btn_MoveUp.winfo_y())
        self.root.update()

        # Move Axis Z Invert
        self.btn_MoveZDown= Tkinter.Button(self.tab_control,image= photo_down, cursor= 'hand2', command= lambda: self.btn_MoveAmountZaxis_click('Down'))
        self.btn_MoveZDown.image= photo_down
        self.btn_MoveZDown.place(x= self.btn_MoveZUp.winfo_x(), y=self.btn_MoveDown.winfo_y())
        self.root.update()

        # ==================================================
        # [TAB CONTROL] Seeding, Watering, Lighting, Grab Image
        # ==================================================
        # Button Seeding
        photo_seed= self.IconResize(gui_vars.saveParaPath+'img_Seed.png')
        self.btn_Seed= Tkinter.Button(self.tab_control,image= photo_seed, cursor= 'hand2', command= self.btn_Seed_click)
        self.btn_Seed.image= photo_seed
        self.btn_Seed.place(x= self.btn_MoveUp.winfo_x()- int(self.btn_MoveUp.winfo_reqwidth()*2)- gui_vars.interval_x, y=self.btn_MoveDown.winfo_y()+ self.btn_MoveDown.winfo_reqheight()+ gui_vars.interval_y*2)
        self.root.update()

        # Button Watering
        photo_water= self.IconResize(gui_vars.saveParaPath+'img_Water.png')
        self.btn_Water= Tkinter.Button(self.tab_control,image= photo_water, cursor= 'hand2', command= self.btn_Water_click)
        self.btn_Water.image= photo_water
        self.btn_Water.place(x= self.btn_Seed.winfo_x()+ int(self.btn_Seed.winfo_reqwidth()*1.5)+ gui_vars.interval_x, y=self.btn_Seed.winfo_y())
        self.root.update()

        # Button Light
        photo_light= self.IconResize(gui_vars.saveParaPath+'img_Light.png')
        self.btn_Light= Tkinter.Button(self.tab_control,image= photo_light, cursor= 'hand2', command= self.btn_Light_click)
        self.btn_Light.image= photo_light
        self.btn_Light.place(x= self.btn_Water.winfo_x()+ int(self.btn_Water.winfo_reqwidth()*1.5)+ gui_vars.interval_x, y=self.btn_Seed.winfo_y())
        self.root.update()

        # Button Take Photo Camera
        photo_cam= self.IconResize(gui_vars.saveParaPath+'img_Cam.png')
        self.btn_CamGrab= Tkinter.Button(self.tab_control,image= photo_cam, cursor= 'hand2', command= self.btn_saveImg_click)
        self.btn_CamGrab.image= photo_cam
        self.btn_CamGrab.place(x= self.btn_Light.winfo_x()+ int(self.btn_Light.winfo_reqwidth()*1.5)+ gui_vars.interval_x, y=self.btn_Seed.winfo_y())
        self.root.update()

        # ==================================================
        # [TAB CONTROL] Move To
        # ==================================================

        self.lbl_Xposs= Tkinter.Label(self.tab_control, text= "MOTOR COORDINATES (MM)".center(30),font= myfont14_Bold)
        self.lbl_Xposs.place(x= gui_vars.interval_x, y = self.btn_Seed.winfo_y()+ self.btn_Seed.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.lbl_Xpos= Tkinter.Label(self.tab_control, text= 'X :',font= myfont12)
        self.lbl_Xpos.place(x= gui_vars.interval_x , y = self.lbl_Xposs.winfo_y()+ self.lbl_Xposs.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_Xpos= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_Xpos.insert(Tkinter.END, "0")
        self.entry_Xpos.place(x= self.lbl_Xpos.winfo_x()+ self.lbl_Xpos.winfo_width(), y= self.lbl_Xpos.winfo_y())
        self.root.update()

        self.lbl_Ypos= Tkinter.Label(self.tab_control, text= 'Y :',font= myfont12)
        self.lbl_Ypos.place(x= self.entry_Xpos.winfo_x()+ self.entry_Xpos.winfo_width()+ gui_vars.interval_x, y = self.lbl_Xpos.winfo_y())
        self.root.update()
        self.entry_Ypos= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_Ypos.insert(Tkinter.END, "0")
        self.entry_Ypos.place(x= self.lbl_Ypos.winfo_x()+ self.lbl_Ypos.winfo_width(), y= self.lbl_Ypos.winfo_y())
        self.root.update()

        self.lbl_Zpos= Tkinter.Label(self.tab_control, text= 'Z :',font= myfont12)
        self.lbl_Zpos.place(x= self.entry_Ypos.winfo_x()+ self.entry_Ypos.winfo_width()+ gui_vars.interval_x, y = self.lbl_Xpos.winfo_y())
        self.root.update()

	self.entry_Zpos= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_Zpos.insert(Tkinter.END, "0")
        self.entry_Zpos.place(x= self.lbl_Zpos.winfo_x()+ self.lbl_Zpos.winfo_width(), y= self.lbl_Zpos.winfo_y())
        self.root.update()

        self.lbl_posUnit= Tkinter.Label(self.tab_control, text=' ')
        self.lbl_posUnit.place(x= self.entry_Zpos.winfo_x()+ self.entry_Zpos.winfo_width(), y= self.entry_Zpos.winfo_y()+gui_vars.interval_y)
        self.root.update()


	self.btn_MoveTo= Tkinter.Button(self.tab_control, text= 'GO', command= self.btn_MoveTo_click,font= myfont10_Bold, bg= self.bgGreen, fg= 'white', activebackground= self.bgGreen_active, activeforeground= 'white')
        self.btn_MoveTo.place(x= self.lbl_posUnit.winfo_x()+ self.lbl_posUnit.winfo_reqwidth()+ gui_vars.interval_x, y=self.lbl_Ypos.winfo_y())
        self.btn_MoveTo.focus_set()
        self.root.update()


        # ==================================================
        # [TAB CONTROL] Scanning Control
        # ==================================================
        self.lbl_Scan= Tkinter.Label(self.tab_control, text="AUTO-SCAN".center(45), font= myfont14_Bold)
        self.lbl_Scan.place(x= gui_vars.interval_x, y= self.btn_MoveTo.winfo_y()+ self.btn_MoveTo.winfo_height()+gui_vars.interval_y)
        self.root.update()


        self.lbl_Scan1stPt= Tkinter.Label(self.tab_control, text= 'Start point'.center(25),font= myfont12_Bold)
        self.lbl_Scan1stPt.place(x= gui_vars.interval_x, y = self.lbl_Scan.winfo_y()+ self.lbl_Scan.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.lbl_Scan1stPt_X= Tkinter.Label(self.tab_control, text= 'X :',font= myfont12_Bold)
        self.lbl_Scan1stPt_X.place(x= gui_vars.interval_x, y = self.lbl_Scan1stPt.winfo_y()+ self.lbl_Scan1stPt.winfo_height()+gui_vars.interval_y)
        self.root.update()


        self.entry_1stXpos= Tkinter.Entry(self.tab_control, font= myfont12, width= 4)
        self.entry_1stXpos.insert(Tkinter.END, '{0}'.format(self.scan_X[0]))
        self.entry_1stXpos.place(x= self.lbl_Scan1stPt_X.winfo_x()+self.lbl_Scan1stPt_X.winfo_width(), y= self.lbl_Scan1stPt_X.winfo_y())
        self.root.update()

        self.lbl_Scan1stPt_Y= Tkinter.Label(self.tab_control, text= 'Y :', font= myfont12_Bold)
        self.lbl_Scan1stPt_Y.place(x=self.entry_1stXpos.winfo_x()+self.entry_1stXpos.winfo_width(), y= self.entry_1stXpos.winfo_y())
        self.root.update()

        self.entry_1stYpos= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_1stYpos.insert(Tkinter.END, '{0}'.format(self.scan_Y[0]))
        self.entry_1stYpos.place(x= self.lbl_Scan1stPt_Y.winfo_x()+self.lbl_Scan1stPt_Y.winfo_width(), y= self.lbl_Scan1stPt_Y.winfo_y())
        self.root.update()

        self.lbl_ScanInterval= Tkinter.Label(self.tab_control, text='Interval'.center(30), font= myfont12_Bold)
        self.lbl_ScanInterval.place(x= self.entry_1stYpos.winfo_x()+ self.entry_1stYpos.winfo_reqwidth()+ gui_vars.interval_x*4, y= self.lbl_Scan1stPt.winfo_y())
        self.root.update()

        self.lbl_Scan2ndPt_X= Tkinter.Label(self.tab_control, text= 'X :',font= myfont12_Bold)
        self.lbl_Scan2ndPt_X.place(x= self.lbl_ScanInterval.winfo_x(), y= self.lbl_ScanInterval.winfo_y()+self.lbl_ScanInterval.winfo_height() + gui_vars.interval_y)
        self.root.update()

        self.entry_ScanInterval_X= Tkinter.Entry(self.tab_control, font=myfont12, width=4)
        self.entry_ScanInterval_X.insert(Tkinter.END, '{0}'.format(self.scan_X[1]))
        self.entry_ScanInterval_X.place(x= self.lbl_Scan2ndPt_X.winfo_x()+self.lbl_Scan2ndPt_X.winfo_width(), y= self.lbl_Scan2ndPt_X.winfo_y())
        self.root.update()

        self.lbl_ScanInterval_comma= Tkinter.Label(self.tab_control, text= 'Y :', font= myfont12_Bold)
        self.lbl_ScanInterval_comma.place(x=self.entry_ScanInterval_X.winfo_x()+self.entry_ScanInterval_X.winfo_width(), y= self.entry_ScanInterval_X.winfo_y())
        self.root.update()

        self.entry_ScanInterval_Y= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_ScanInterval_Y.insert(Tkinter.END, '{0}'.format(self.scan_Y[1]))
        self.entry_ScanInterval_Y.place(x= self.lbl_ScanInterval_comma.winfo_x()+self.lbl_ScanInterval_comma.winfo_width(), y= self.lbl_ScanInterval_comma.winfo_y())
        self.root.update()

        self.lbl_ScanAmount= Tkinter.Label(self.tab_control, text='Scanning Step'.center(18), font= myfont12_Bold)
        self.lbl_ScanAmount.place(x= gui_vars.interval_x, y= self.entry_1stXpos.winfo_y()+ self.entry_1stXpos.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.lbl_Scan3rdPt_X = Tkinter.Label(self.tab_control, text= 'X :', font= myfont12_Bold)
        self.lbl_Scan3rdPt_X.place(x= self.lbl_ScanAmount.winfo_x(), y= self.lbl_ScanAmount.winfo_y()+self.lbl_ScanAmount.winfo_height() + gui_vars.interval_y)
        self.root.update()

        self.entry_ScanAmount_X= Tkinter.Entry(self.tab_control, font=myfont12, width=4)
        self.entry_ScanAmount_X.insert(Tkinter.END, '{0}'.format(self.scan_X[2]))
        self.entry_ScanAmount_X.place(x= self.lbl_Scan3rdPt_X.winfo_x() + self.lbl_Scan3rdPt_X.winfo_width(), y=self.lbl_Scan3rdPt_X.winfo_y())
        self.root.update()

        self.lbl_ScanAmount_comma= Tkinter.Label(self.tab_control, text= 'Y :', font= myfont12_Bold)
        self.lbl_ScanAmount_comma.place(x=self.entry_ScanAmount_X.winfo_x()+self.entry_ScanAmount_X.winfo_width(),y= self.entry_ScanAmount_X.winfo_y())
        self.root.update()

        self.entry_ScanAmount_Y= Tkinter.Entry(self.tab_control, font= myfont12, width=4)
        self.entry_ScanAmount_Y.insert(Tkinter.END, '{0}'.format(self.scan_Y[2]))
        self.entry_ScanAmount_Y.place(x= self.lbl_ScanAmount_comma.winfo_x()+self.lbl_ScanAmount_comma.winfo_width(), y= self.lbl_ScanAmount_comma.winfo_y())
        self.root.update()

        self.btn_StartScan= Tkinter.Button(self.tab_control, text= 'Start Scan', command= self.btn_StartScan_click,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_StartScan.place(x= self.entry_ScanAmount_Y.winfo_x()*1.5+20, y=self.entry_ScanAmount_Y.winfo_y() - gui_vars.interval_y)
        self.root.update()


        # ==================================================
        # [TAB CONTROL] Status
        # ==================================================

        self.lbl_Status= Tkinter.Label(self.tab_control, text="STATUS".center(50), font= myfont14_Bold)
        self.lbl_Status.place(x= gui_vars.interval_x, y= self.btn_StartScan.winfo_y()+ self.btn_StartScan.winfo_height()+gui_vars.interval_y)
        self.root.update()

        #Status Indicator Water
        self.Indi_Water= Tkinter.Label(self.tab_control, text= 'Water :', font=myfont12_Bold)
        self.Indi_Water.place(x= gui_vars.interval_x * 6, y=self.lbl_Status.winfo_y()+ self.lbl_Status.winfo_height()+ gui_vars.interval_y)
        self.root.update()
        self.btn_Indi_Water= Tkinter.Button(self.tab_control, text='Off', font= myfont12_Bold, fg= 'white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed)
        self.btn_Indi_Water.place (x= self.Indi_Water.winfo_x() + self.Indi_Water.winfo_width()+ gui_vars.interval_x, y=self.lbl_Status.winfo_y()+ self.lbl_Status.winfo_height())
        self.root.update()

        #Status Indicator Vaccum
        self.Indi_Seed= Tkinter.Label(self.tab_control, text= 'Vaccum : ', font=myfont12_Bold)
        self.Indi_Seed.place(x= self.btn_Indi_Water.winfo_x()+ self.btn_Indi_Water.winfo_width() + gui_vars.interval_x*3, y= self.lbl_Status.winfo_y()+ self.lbl_Status.winfo_height()+ gui_vars.interval_y)
        self.root.update()
        self.btn_Indi_Seed= Tkinter.Button(self.tab_control, text='Off', font=myfont12_Bold, fg='white', activeforeground='white', bg= self.bgRed, activebackground=self.bgRed)
        self.btn_Indi_Seed.place(x=self.Indi_Seed.winfo_x()+ self.Indi_Seed.winfo_width(), y= self.lbl_Status.winfo_y() + self.lbl_Status.winfo_height())
        self.root.update()

        #Status Indicator Light
        self.Indi_Light= Tkinter.Label(self.tab_control, text='Light  :', font=myfont12_Bold)
        self.Indi_Light.place(x= self.Indi_Water.winfo_x() , y=self.btn_Indi_Water.winfo_y()+self.btn_Indi_Water.winfo_height() + gui_vars.interval_y)
        self.root.update()
        self.btn_Indi_Light= Tkinter.Button(self.tab_control, text='Off', font= myfont12_Bold, fg= 'white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed)
        self.btn_Indi_Light.place (x= self.Indi_Light.winfo_x() + self.Indi_Light.winfo_width()+ gui_vars.interval_x, y=self.btn_Indi_Water.winfo_y()+self.btn_Indi_Water.winfo_height() + gui_vars.interval_y)
        self.root.update()

        self.lbl_Soil_Data= Tkinter.Label(self.tab_control, text='0%' , font=myfont12_Bold)
        self.lbl_Soil_Data.place(x= self.btn_Indi_Light.winfo_x() + self.btn_Indi_Light.winfo_width() , y=self.btn_Indi_Light.winfo_y()  )
        self.root.update()

        # ==================================================
        # [TAB LOAD SCRIPT]
        # ==================================================
        self.lbl_loadscript= Tkinter.Label(self.tab_loadscript, text="Load & Run Script".center(45), font= myfont14_Bold)
        self.lbl_loadscript.place(x= gui_vars.interval_x, y= gui_vars.interval_y)
        self.root.update()

        self.entry_scriptPath= Tkinter.Entry(self.tab_loadscript, font= myfont12, width=25)
        self.entry_scriptPath.insert(Tkinter.END, self.scriptPath)
        self.entry_scriptPath.place(x= self.lbl_loadscript.winfo_x(), y= self.lbl_loadscript.winfo_y()+ self.lbl_loadscript.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()

        self.btn_choosescript= Tkinter.Button(self.tab_loadscript, text='Choose', command= self.btn_choosescript_click, font= myfont8_Bold, width=0, height=0, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active)
        self.btn_choosescript.place(x= self.entry_scriptPath.winfo_x()+ self.entry_scriptPath.winfo_reqwidth()+ gui_vars.interval_x, y= self.entry_scriptPath.winfo_y())
        self.root.update()

        self.btn_loadscript= Tkinter.Button(self.tab_loadscript, text='Load', command= self.btn_loadscript_click, font= myfont12_Bold, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active)
        self.btn_loadscript.place(x= self.entry_scriptPath.winfo_x(), y= self.entry_scriptPath.winfo_y()+ self.entry_scriptPath.winfo_reqheight()+ gui_vars.interval_y)
        self.root.update()
        self.btn_savescript= Tkinter.Button(self.tab_loadscript, text='Save', command= self.btn_savescript_click, font= myfont12_Bold, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active)
        self.btn_savescript.place(x= self.btn_loadscript.winfo_x()+ self.btn_loadscript.winfo_reqwidth()+ gui_vars.interval_x*2, y= self.btn_loadscript.winfo_y())
        self.root.update()
        self.btn_runscript= Tkinter.Button(self.tab_loadscript, text='RUN', command= self.btn_runscript_click, font= myfont12_Bold, fg= 'white', activeforeground='white', bg= self.bgGreen, activebackground= self.bgGreen_active)
        self.btn_runscript.place(x= self.btn_savescript.winfo_x()+ self.btn_savescript.winfo_reqwidth()+ gui_vars.interval_x*2, y= self.btn_savescript.winfo_y())
        self.btn_runscript.focus_set()
        self.root.update()

        #self.txtbox_script = ScrolledText.ScrolledText(self.tab_loadscript, width=40, height= 30 ,font = myfont10, bd = 2, relief = RIDGE, vscrollmode= 'dynamic')
        self.txtbox_script = Pmw.ScrolledText(self.tab_loadscript, text_width=36, text_height= 20, hscrollmode= 'dynamic', vscrollmode= 'static', text_wrap= 'none', labelpos= 'n', label_text= "Script")#, rowheader= 1)
        self.txtbox_script.place(x= self.btn_loadscript.winfo_x(), y= self.btn_loadscript.winfo_y()+ self.btn_loadscript.winfo_reqheight()+ gui_vars.interval_y)

        # ==================================================
        # [TAB EVENT SCHEDULE]
        # ==================================================
        #Event Schedule 1
        self.lbl_schedule= Tkinter.Label(self.tab_event_schedule, text="Event Schedule 1", font= myfont14_Bold, width= 30,fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active) #, command= self.show_hide_Event_Schedule1
        self.lbl_schedule.place(x= gui_vars.interval_x , y= gui_vars.interval_y)
        self.root.update()

        self.lbl_Action= Tkinter.Label(self.tab_event_schedule, text= 'Action :',font= myfont12_Bold)
        self.lbl_Action.place(x= gui_vars.interval_x, y = self.lbl_schedule.winfo_y()+ self.lbl_schedule.winfo_height()+gui_vars.interval_y)
        self.root.update()

        Action = ['Watering','Scanning']
        tkvar11.set(Action[0])
        self.entry_Action = OptionMenu(self.tab_event_schedule, tkvar11, *Action)
        self.entry_Action.place(x= self.lbl_Action.winfo_x()+self.lbl_Action.winfo_width(), y= self.lbl_Action.winfo_y()-5)
        self.root.update()
        tkvar11.trace('w', self.change_dropdown11)

        self.lbl_X_Schedule= Tkinter.Label(self.tab_event_schedule, text= 'Interval X :',font= myfont12_Bold)
        self.lbl_X_Schedule.place(x= gui_vars.interval_x , y = self.entry_Action.winfo_y()+ self.entry_Action.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_X_Schedule= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_X_Schedule.insert(Tkinter.END, "0")
        self.entry_X_Schedule.place(x= self.lbl_X_Schedule.winfo_x()+ self.lbl_X_Schedule.winfo_width(), y= self.lbl_X_Schedule.winfo_y())
        self.root.update()

        self.lbl_Y_Schedule= Tkinter.Label(self.tab_event_schedule, text= ', Y :',font= myfont12_Bold)
        self.lbl_Y_Schedule.place(x= self.entry_X_Schedule.winfo_x()+ self.entry_X_Schedule.winfo_width()+ gui_vars.interval_x, y = self.lbl_X_Schedule.winfo_y())
        self.root.update()

        self.entry_Y_Schedule= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_Y_Schedule.insert(Tkinter.END, "0")
        self.entry_Y_Schedule.place(x= self.lbl_Y_Schedule.winfo_x()+ self.lbl_Y_Schedule.winfo_width(), y= self.lbl_Y_Schedule.winfo_y())
        self.root.update()

        self.lbl_water_amount= Tkinter.Label(self.tab_event_schedule, text= '| Water :',font= myfont12_Bold)
        self.lbl_water_amount.place(x= self.entry_Y_Schedule.winfo_x()+ self.entry_Y_Schedule.winfo_width()+ gui_vars.interval_x, y = self.entry_Y_Schedule.winfo_y())
        self.root.update()

	self.entry_water_amount= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_water_amount.insert(Tkinter.END, "0")
        self.entry_water_amount.place(x= self.lbl_water_amount.winfo_x()+ self.lbl_water_amount.winfo_width(), y= self.lbl_water_amount.winfo_y())
        self.root.update()


        self.lbl_Start= Tkinter.Label(self.tab_event_schedule, text= 'Time, Repeat :',font= myfont12_Bold)
        self.lbl_Start.place(x= gui_vars.interval_x, y = self.entry_water_amount.winfo_y()+ self.entry_water_amount.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_Time= Tkinter.Entry(self.tab_event_schedule,  font= myfont12_Bold, width= 6)
        self.entry_Time.insert(Tkinter.END, '00:00')
        self.entry_Time.place(x= self.lbl_Start.winfo_x()+self.lbl_Start.winfo_width(), y= self.lbl_Start.winfo_y())
        self.root.update()

        self.lbl_Schedule_comma= Tkinter.Label(self.tab_event_schedule, text= ', ', font= myfont12_Bold)
        self.lbl_Schedule_comma.place(x=self.entry_Time.winfo_x()+self.entry_Time.winfo_width(),y= self.entry_Time.winfo_y())
        self.root.update()

        Repeat = ['Every Day', 'Every Hour', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', ' Friday', 'Saturday']
        tkvar12.set(Repeat[0])
        self.entry_Repeat = OptionMenu(self.tab_event_schedule, tkvar12, *Repeat)
        self.root.update()
        self.entry_Repeat.place(x= self.lbl_Schedule_comma.winfo_x()+self.lbl_Schedule_comma.winfo_width(), y= self.lbl_Schedule_comma.winfo_y()-5)
        tkvar12.trace('w', self.change_dropdown12)
        self.root.update()

        self.btn_Schedule_Go= Tkinter.Button(self.tab_event_schedule, text= 'Go', command= self.run_schedule_1,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_Schedule_Go.place(x= gui_vars.interval_x * 18, y = self.entry_Repeat.winfo_y()+ self.entry_Repeat.winfo_height()+gui_vars.interval_y)
        self.root.update()

        # Event Schedule 2
        self.lbl_schedule_2= Tkinter.Label(self.tab_event_schedule, text="Event Schedule 2", font= myfont14_Bold, width= 30, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active)# command= self.show_hide_Event_Schedule2)
        self.lbl_schedule_2.place(x= gui_vars.interval_x, y = self.btn_Schedule_Go.winfo_y()+ self.btn_Schedule_Go.winfo_height()+gui_vars.interval_y)
        self.root.update()


        self.lbl_Action_2= Tkinter.Label(self.tab_event_schedule, text= 'Action :',font= myfont12_Bold)
        self.lbl_Action_2.place(x= gui_vars.interval_x, y = self.lbl_schedule_2.winfo_y()+ self.lbl_schedule_2.winfo_height()+gui_vars.interval_y)
        self.root.update()

        Action = ['Watering','Scanning']
        tkvar21.set(Action[0])
        self.entry_Action_2 = OptionMenu(self.tab_event_schedule, tkvar21, *Action)
        self.entry_Action_2.place(x= self.lbl_Action_2.winfo_x()+self.lbl_Action_2.winfo_width(), y= self.lbl_Action_2.winfo_y()-5)
        self.root.update()
        tkvar21.trace('w', self.change_dropdown21)

        self.lbl_X_Schedule_2= Tkinter.Label(self.tab_event_schedule, text= 'Interval X :',font= myfont12_Bold)
        self.lbl_X_Schedule_2.place(x= gui_vars.interval_x , y = self.entry_Action_2.winfo_y()+ self.entry_Action_2.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_X_Schedule_2= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_X_Schedule_2.insert(Tkinter.END, "0")
        self.entry_X_Schedule_2.place(x= self.lbl_X_Schedule_2.winfo_x()+ self.lbl_X_Schedule_2.winfo_width(), y= self.lbl_X_Schedule_2.winfo_y())
        self.root.update()

        self.lbl_Y_Schedule_2= Tkinter.Label(self.tab_event_schedule, text= ', Y :',font= myfont12_Bold)
        self.lbl_Y_Schedule_2.place(x= self.entry_X_Schedule_2.winfo_x()+ self.entry_X_Schedule_2.winfo_width()+ gui_vars.interval_x, y = self.lbl_X_Schedule_2.winfo_y())
        self.root.update()

        self.entry_Y_Schedule_2= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_Y_Schedule_2.insert(Tkinter.END, "0")
        self.entry_Y_Schedule_2.place(x= self.lbl_Y_Schedule_2.winfo_x()+ self.lbl_Y_Schedule_2.winfo_width(), y= self.lbl_Y_Schedule_2.winfo_y())
        self.root.update()

        self.lbl_water_amount_2= Tkinter.Label(self.tab_event_schedule, text= '| Water :',font= myfont12_Bold)
        self.lbl_water_amount_2.place(x= self.entry_Y_Schedule_2.winfo_x()+ self.entry_Y_Schedule_2.winfo_width()+ gui_vars.interval_x, y = self.entry_Y_Schedule_2.winfo_y())
        self.root.update()

	self.entry_water_amount_2= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_water_amount_2.insert(Tkinter.END, "0")
        self.entry_water_amount_2.place(x= self.lbl_water_amount_2.winfo_x()+ self.lbl_water_amount_2.winfo_width(), y= self.lbl_water_amount_2.winfo_y())
        self.root.update()

        self.lbl_Start_2= Tkinter.Label(self.tab_event_schedule, text= 'Time, Repeat :',font= myfont12_Bold)
        self.lbl_Start_2.place(x= gui_vars.interval_x, y = self.entry_water_amount_2.winfo_y()+ self.entry_water_amount_2.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_Time_2= Tkinter.Entry(self.tab_event_schedule,  font= myfont12_Bold, width= 6)
        self.entry_Time_2.insert(Tkinter.END, '00:00')
        self.entry_Time_2.place(x= self.lbl_Start_2.winfo_x()+self.lbl_Start_2.winfo_width(), y= self.lbl_Start_2.winfo_y())
        self.root.update()

        self.lbl_Schedule_comma_2= Tkinter.Label(self.tab_event_schedule, text= ', ', font= myfont12_Bold)
        self.lbl_Schedule_comma_2.place(x=self.entry_Time_2.winfo_x()+self.entry_Time_2.winfo_width(),y= self.entry_Time_2.winfo_y())
        self.root.update()

        Repeat = ['Every Day', 'Every Hour', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', ' Friday', 'Saturday']
        tkvar22.set(Repeat[0])
        self.entry_Repeat_2 = OptionMenu(self.tab_event_schedule, tkvar22, *Repeat)
        self.entry_Repeat_2.place(x= self.lbl_Schedule_comma_2.winfo_x()+self.lbl_Schedule_comma_2.winfo_width(), y= self.lbl_Schedule_comma_2.winfo_y()-5)
        tkvar22.trace('w', self.change_dropdown22)
        self.root.update()

        self.btn_Schedule_Go_2= Tkinter.Button(self.tab_event_schedule, text= 'Go', command= self.run_schedule_2,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_Schedule_Go_2.place(x= gui_vars.interval_x * 18, y = self.entry_Repeat_2.winfo_y()+ self.entry_Repeat_2.winfo_height()+gui_vars.interval_y)
        self.root.update()

        # Event Schedule 3
        self.lbl_schedule_3= Tkinter.Label(self.tab_event_schedule, text="Event Schedule 3", font= myfont14_Bold, width= 30, fg= 'white', activeforeground='white', bg= bgGray)# command= self.show_hide_Event_Schedule3)
        self.lbl_schedule_3.place(x= gui_vars.interval_x, y = self.btn_Schedule_Go_2.winfo_y()+ self.btn_Schedule_Go_2.winfo_height()+gui_vars.interval_y)
        self.root.update()


        self.lbl_Action_3= Tkinter.Label(self.tab_event_schedule, text= 'Action :',font= myfont12_Bold)
        self.lbl_Action_3.place(x= gui_vars.interval_x, y = self.lbl_schedule_3.winfo_y()+ self.lbl_schedule_3.winfo_height()+gui_vars.interval_y)
        self.root.update()

        Action = ['Watering','Monitoring']
        tkvar31.set(Action[0])
        self.entry_Action_3 = OptionMenu(self.tab_event_schedule, tkvar31, *Action)
        self.entry_Action_3.place(x= self.lbl_Action_3.winfo_x()+self.lbl_Action_3.winfo_width(), y= self.lbl_Action_3.winfo_y()-5)
        self.root.update()
        tkvar31.trace('w', self.change_dropdown31)

        self.lbl_X_Schedule_3= Tkinter.Label(self.tab_event_schedule, text= 'Interval X :',font= myfont12_Bold)
        self.lbl_X_Schedule_3.place(x= gui_vars.interval_x , y = self.entry_Action_3.winfo_y()+ self.entry_Action_3.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_X_Schedule_3= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_X_Schedule_3.insert(Tkinter.END, "0")
        self.entry_X_Schedule_3.place(x= self.lbl_X_Schedule_3.winfo_x()+ self.lbl_X_Schedule_3.winfo_width(), y= self.lbl_X_Schedule_3.winfo_y())
        self.root.update()

        self.lbl_Y_Schedule_3= Tkinter.Label(self.tab_event_schedule, text= ', Y :',font= myfont12_Bold)
        self.lbl_Y_Schedule_3.place(x= self.entry_X_Schedule_3.winfo_x()+ self.entry_X_Schedule_3.winfo_width()+ gui_vars.interval_x, y = self.lbl_X_Schedule_3.winfo_y())
        self.root.update()

        self.entry_Y_Schedule_3= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_Y_Schedule_3.insert(Tkinter.END, "0")
        self.entry_Y_Schedule_3.place(x= self.lbl_Y_Schedule_3.winfo_x()+ self.lbl_Y_Schedule_3.winfo_width(), y= self.lbl_Y_Schedule_3.winfo_y())
        self.root.update()

        self.lbl_water_amount_3= Tkinter.Label(self.tab_event_schedule, text= '| Water :',font= myfont12_Bold)
        self.lbl_water_amount_3.place(x= self.entry_Y_Schedule_3.winfo_x()+ self.entry_Y_Schedule_3.winfo_width()+ gui_vars.interval_x, y = self.entry_Y_Schedule_3.winfo_y())
        self.root.update()

	self.entry_water_amount_3= Tkinter.Entry(self.tab_event_schedule, font= myfont12_Bold, width=3)
        self.entry_water_amount_3.insert(Tkinter.END, "0")
        self.entry_water_amount_3.place(x= self.lbl_water_amount_3.winfo_x()+ self.lbl_water_amount_3.winfo_width(), y= self.lbl_water_amount_3.winfo_y())
        self.root.update()

        self.lbl_Start_3= Tkinter.Label(self.tab_event_schedule, text= 'Time, Repeat :',font= myfont12_Bold)
        self.lbl_Start_3.place(x= gui_vars.interval_x, y = self.entry_water_amount_3.winfo_y()+ self.entry_water_amount_3.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_Time_3= Tkinter.Entry(self.tab_event_schedule,  font= myfont12_Bold, width= 6)
        self.entry_Time_3.insert(Tkinter.END, '00:00')
        self.entry_Time_3.place(x= self.lbl_Start_3.winfo_x()+self.lbl_Start_3.winfo_width(), y= self.lbl_Start_3.winfo_y())
        self.root.update()

        self.lbl_Schedule_comma_3= Tkinter.Label(self.tab_event_schedule, text= ', ', font= myfont12_Bold)
        self.lbl_Schedule_comma_3.place(x=self.entry_Time_3.winfo_x()+self.entry_Time_3.winfo_width(),y= self.entry_Time_3.winfo_y())
        self.root.update()

        Repeat = ['Every Day', 'Every Hour', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', ' Friday', 'Saturday']
        tkvar32.set(Repeat[0])
        self.entry_Repeat_3 = OptionMenu(self.tab_event_schedule, tkvar32, *Repeat)
        self.entry_Repeat_3.place(x= self.lbl_Schedule_comma_3.winfo_x()+self.lbl_Schedule_comma_3.winfo_width(), y= self.lbl_Schedule_comma_3.winfo_y()-5)
        tkvar32.trace('w', self.change_dropdown32)
        self.root.update()

        self.btn_Schedule_Go_3= Tkinter.Button(self.tab_event_schedule, text= 'Go', command= self.run_schedule_3,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_Schedule_Go_3.place(x= gui_vars.interval_x * 18, y = self.entry_Repeat_3.winfo_y()+ self.entry_Repeat_3.winfo_height()+gui_vars.interval_y)
        self.root.update()

        # ==================================================
        # [TAB DATABASE PLANTING]
        # ==================================================
        self.lbl_planting = Tkinter.Label(self.tab_planting, text="INPUT PLANTING", font= myfont14_Bold, width= 30, fg= 'white', activeforeground='white', bg= bgGray, activebackground= bgGray_active) #, command= self.show_hide_Event_Schedule1
        self.lbl_planting.place(x= gui_vars.interval_x , y= gui_vars.interval_y)
        self.root.update()

        self.lbl_name_plant = Tkinter.Label(self.tab_planting, text= 'Name Plant     : ',font= myfont12_Bold)
        self.lbl_name_plant.place(x= gui_vars.interval_x , y = self.lbl_planting.winfo_y()+ self.lbl_planting.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.entry_name_plant = Tkinter.Entry(self.tab_planting, font= myfont12_Bold, width=14, textvariable = NAME_PLANT)
        self.entry_name_plant.place(x= self.lbl_name_plant.winfo_x()+ self.lbl_name_plant.winfo_width(), y= self.lbl_name_plant.winfo_y())
        self.root.update()

        self.lbl_location_planting_X = Tkinter.Label(self.tab_planting, text="Location X, Y : ", font=myfont12_Bold)
        self.lbl_location_planting_X.place(x= gui_vars.interval_x, y=self.entry_name_plant.winfo_y()+ self.entry_name_plant.winfo_height()+ gui_vars.interval_y)
        self.root.update()

        self.entry_location_planting_X = Tkinter.Entry(self.tab_planting, font= myfont12_Bold, width=6, textvariable= LOCATION_PLANT_X)
        self.entry_location_planting_X.insert(Tkinter.END, "0")
        self.entry_location_planting_X.place(x= self.lbl_location_planting_X.winfo_x()+ self.lbl_location_planting_X.winfo_width(), y= self.lbl_location_planting_X.winfo_y())
        self.root.update()

        self.lbl_location_planting_Y = Tkinter.Label(self.tab_planting, text= ' , ',font= myfont12_Bold)
        self.lbl_location_planting_Y.place(x= self.entry_location_planting_X.winfo_x()+ self.entry_location_planting_X.winfo_width(), y = self.lbl_location_planting_X.winfo_y())
        self.root.update()

        self.entry_location_planting_Y = Tkinter.Entry(self.tab_planting, font= myfont12_Bold, width=6, textvariable = LOCATION_PLANT_Y)
        self.entry_location_planting_Y.insert(Tkinter.END, "0")
        self.entry_location_planting_Y.place(x= self.lbl_location_planting_Y.winfo_x()+ self.lbl_location_planting_Y.winfo_width(), y= self.lbl_location_planting_X.winfo_y())
        self.root.update()

        self.lbl_note_plant = Tkinter.Label(self.tab_planting, text = 'Note Plant      :', font = myfont12_Bold )
        self.lbl_note_plant.place(x= gui_vars.interval_x, y=self.entry_location_planting_Y.winfo_y() + self.entry_location_planting_Y.winfo_height()+ gui_vars.interval_y)
        self.root.update()

        self.entry_note_plant = Tkinter.Entry(self.tab_planting, font= myfont12_Bold, width =18, textvariable = NOTE_PLANT)
        self.entry_note_plant.insert(Tkinter.END, "")
        self.entry_note_plant.place(x= self.lbl_note_plant.winfo_x()+ self.lbl_note_plant.winfo_width(), y= self.lbl_note_plant.winfo_y())
        self.root.update()

        self.btn_Planting = Tkinter.Button(self.tab_planting, text= 'Insert / Go', command= self.DatabaseAdd,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_Planting.place(x= gui_vars.interval_x * 7, y = self.entry_note_plant.winfo_y()+ self.entry_note_plant.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.btn_View_Plant = Tkinter.Button(self.tab_planting, text= 'View Plant', command= self.Viewall,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_View_Plant.place(x= self.btn_Planting.winfo_x()+ self.btn_Planting.winfo_reqwidth()+ gui_vars.interval_x*2, y= self.btn_Planting.winfo_y())
        self.root.update()

        self.btn_UpdateButton = Tkinter.Button(self.tab_planting,text='Update',command=self.Update_data,font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_UpdateButton.place(x= gui_vars.interval_x * 7, y = self.btn_View_Plant.winfo_y()+ self.btn_View_Plant.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.btn_DeleteButton = Tkinter.Button(self.tab_planting,text='Delete',command=self.Delete_data, font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height)
        self.btn_DeleteButton.place(x= self.btn_UpdateButton.winfo_x()+ self.btn_UpdateButton.winfo_reqwidth()+ gui_vars.interval_x*2, y= self.btn_UpdateButton.winfo_y())
        self.root.update

        # ==================================================
        # [TAB IMAGE PROCASSING]
        # ==================================================
        self.lbl_image_process= Tkinter.Label(self.tab_planting, text="Image Processing", font= myfont14_Bold, width= 30, fg= 'white', activeforeground='white', bg= bgGray)# command= self.show_hide_Event_Schedule3)
        self.lbl_image_process.place(x= gui_vars.interval_x, y = self.btn_UpdateButton.winfo_y()+ self.btn_UpdateButton.winfo_height()+gui_vars.interval_y)
        self.root.update()

        self.btn_saveImg= Tkinter.Button(self.tab_planting, text='Save Image', command= self.btn_saveImg_click,font= myfont14, width= btn_width, height= btn_height)
        self.btn_saveImg.place(x= gui_vars.interval_x *7, y= self.lbl_image_process.winfo_y()+ self.lbl_image_process.winfo_height()+ gui_vars.interval_y)
        self.root.update()

        self.btn_loadImg= Tkinter.Button(self.tab_planting, text='Load Image', command= self.btn_loadImg_click, font= myfont14, width=btn_width, height=btn_height)
        self.btn_loadImg.place(x= self.btn_saveImg.winfo_x() + self.btn_saveImg.winfo_reqwidth()+ gui_vars.interval_x, y=self.btn_saveImg.winfo_y())
        self.root.update()

        self.btn_Plant_Detection= Tkinter.Button(self.tab_planting, text='Plant Detection', command= self.Plant_Detection_Go,font= myfont14, width= btn_width + 5 , height= btn_height)
        self.btn_Plant_Detection.place(x= gui_vars.interval_x*12, y= self.btn_loadImg.winfo_y()+ self.btn_loadImg.winfo_height()+ gui_vars.interval_y)
        self.root.update()


        '''self.lbl_green_plant_detect= Tkinter.Label(self.tab_planting, text="Detect Green Plant", font= myfont14_Bold)
        self.lbl_green_plant_detect.place(x= gui_vars.interval_x, y= self.btn_loadImg.winfo_y()+ self.btn_loadImg.winfo_height()+ gui_vars.interval_y + 5)
        self.root.update()

        self.btn_plant_detect= Tkinter.Button(self.tab_planting, text='Detect',font= myfont14_Bold, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active, width= btn_width, height= btn_height,command= self.detectGreenPlant)
        self.btn_plant_detect.place(x= self.lbl_green_plant_detect.winfo_x()+ self.lbl_green_plant_detect.winfo_reqwidth()+ gui_vars.interval_x, y= self.btn_loadImg.winfo_y()+ self.btn_loadImg.winfo_height()+ gui_vars.interval_y)
        self.root.update()

        #=============================================
        # [group] Plant Index
        #=============================================
        self.grp_PlantIndex= Tkinter.LabelFrame(self.tab_planting, text= 'Plant Index', font=myfont12_Bold, width=Left_width-gui_vars.interval_x*2 ,height=50, relief=Tkinter.RIDGE, padx=0, pady=0 )

        y_rdbox= self.btn_plant_detect.winfo_y()+ self.btn_plant_detect.winfo_height()+ gui_vars.interval_y
        self.lst_PlantIndex_rdbox = list()
        self.PlantIndex= Tkinter.IntVar()
        for idx, name in enumerate(gui_vars.rdbox_PlantIndexItem):
            self.lst_PlantIndex_rdbox.append(Tkinter.Radiobutton(self.grp_PlantIndex, text = name, font=myfont12, value=idx, variable = self.PlantIndex, indicatoron=1, command= self.rdbtn_PlantINdex_click))
            self.lst_PlantIndex_rdbox[idx].place(x= gui_vars.interval_x * 5 + gui_vars.interval_rdbox*idx*1.2, y=0)
        self.lst_PlantIndex_rdbox[0].select()
        self.grp_PlantIndex.place(x= gui_vars.interval_x, y=y_rdbox)
        self.root.update()



        #=============================================
        # [group] Binary Method
        #=============================================
        self.grp_BinaryMethod= Tkinter.LabelFrame(self.tab_planting, text= 'Binary Method', font=myfont12_Bold, width=Left_width-gui_vars.interval_x*2 ,height=50, relief=Tkinter.RIDGE, padx=0, pady=0)#, font= self.__myfont12_Bold)

        self.lst_BinaryMethod_rdbox = list()
        self.BinaryMethodIndex= Tkinter.IntVar()
        for idx, name in enumerate(gui_vars.rdbox_BinaryMethodItem):
            self.lst_BinaryMethod_rdbox.append(Tkinter.Radiobutton(self.grp_BinaryMethod, text = name, font=myfont12, value=idx, variable = self.BinaryMethodIndex, indicatoron=1, command= self.rdbtn_BinaryMethodIndex_click))
            self.lst_BinaryMethod_rdbox[idx].place(x= gui_vars.interval_x * 3 + (gui_vars.interval_rdbox+9)*idx*1.2 , y=0)
        self.lst_BinaryMethod_rdbox[0].select()
        self.grp_BinaryMethod.place(x= gui_vars.interval_x, y=self.grp_PlantIndex.winfo_y()+ self.grp_PlantIndex.winfo_reqheight()+ gui_vars.interval_y*1)
        self.root.update()

        self.scale_threshold_graylevel = Tkinter.Scale(self.tab_planting , from_= 0 , to = 255 , orient = Tkinter.HORIZONTAL , label = "Gray Level", font = myfont12_Bold, width = 7, length = 150 )
        self.scale_threshold_graylevel.set(self.threshold_graylevel)
        self.scale_threshold_graylevel.place(x= self.grp_BinaryMethod.winfo_x(), y= self.grp_BinaryMethod.winfo_y()+ self.grp_BinaryMethod.winfo_reqheight() + gui_vars.interval_y)
        #self.scale_threshold_graylevel.config(state= 'disabled')
        self.root.update()

        self.btn_Method_OtsuBinary= Tkinter.Button(self.tab_planting, text='Otsu Binary', command=self.method_OtsuBinary, font= myfont14, width = btn_width, height = btn_height)
        self.btn_Method_OtsuBinary.place(x= self.scale_threshold_graylevel.winfo_x()+ self.scale_threshold_graylevel.winfo_reqwidth()+ gui_vars.interval_x, y= self.scale_threshold_graylevel.winfo_y())
        self.root.update()

        self.scale_threshold_MinSize = Tkinter.Scale(self.tab_planting, from_ = 0 , to = 99999 , orient = Tkinter.HORIZONTAL , label = "Min Contour Size".center(15), font = myfont12_Bold, width = 7, length = 150 )
        self.scale_threshold_MinSize.set(self.threshold_MinSize)
        self.scale_threshold_MinSize.place(x= self.scale_threshold_graylevel.winfo_x(), y= self.scale_threshold_graylevel.winfo_y()+ self.scale_threshold_graylevel.winfo_height())
        self.root.update()
        self.scale_threshold_MaxSize = Tkinter.Scale(self.tab_planting, from_ = 0 , to = 99999 , orient = Tkinter.HORIZONTAL , label = "Max Contour Size".center(15), font = myfont12_Bold, width = 7, length = 150 )
        self.scale_threshold_MaxSize.set(self.threshold_MaxSize)
        self.scale_threshold_MaxSize.place(x= self.scale_threshold_MinSize.winfo_x() + self.scale_threshold_MinSize.winfo_reqwidth()+ gui_vars.interval_x, y=self.scale_threshold_MinSize.winfo_y())
        '''

        # ==================================================
        # [ROOT] Main Image Frame
        # ==================================================

        #self.frame_width, self.frame_height= int(0.5*(self.screen_width-Left_width- gui_vars.interval_x*2)), int(0.5*(self.screen_height-self.FileMenu.winfo_reqheight()- self.statuslabel.winfo_reqheight() -gui_vars.interval_y*2))
        self.frame_width, self.frame_height= int((self.screen_width-Left_width- gui_vars.interval_x*2)/3), int(0.5*(self.screen_height- self.statuslabel.winfo_reqheight() -gui_vars.interval_y*1))

        print '*** Frame w,h: ',self.frame_width, self.frame_height
        self.frame= np.zeros((int(self.frame_height), int(self.frame_width),3),np.uint8)
        cv2.putText(self.frame, '3',(10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)

        result = Image.fromarray(self.frame)
        result = ImageTk.PhotoImage(result)
        #result = Canvas(width= self.frame_width, height= self.frame_height)
        self.panel = Tkinter.Label(self.root , image = result)
        self.panel.image = result
        #self.grid(result, 10)
        self.panel.place(x=Left_width+gui_vars.interval_x, y= 0)
        self.root.update()


        # ==================================================
        # [ROOT] Display merge Image Frame
        # ==================================================
        self.mergeframe_width, self.mergeframe_height= self.frame_width*2, self.frame_height*2+2
        self.mergeframe= np.zeros((int(self.mergeframe_height), int(self.mergeframe_width), 3),np.uint8)

        cv2.putText(self.mergeframe, '1',(10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)

        result = Image.fromarray(self.mergeframe)
        result = ImageTk.PhotoImage(result)
        self.panel_mergeframe = Tkinter.Label(self.root, image = result)
        self.panel_mergeframe.image = result
        self.panel_mergeframe.place(x=self.panel.winfo_x()+ self.panel.winfo_reqwidth(), y= 0)
        #B w = Canvas(width= self.mergeframe_width,
        #B           height= self.mergeframe_height)
        #B self.grid(w, 100)
        #B w.place(x=self.panel.winfo_x()+ self.panel.winfo_reqwidth(), y=0)
        self.root.update()

        # ==================================================
        # [ROOT] One Shot Image Frame
        # ==================================================
        self.singleframe_width, self.singleframe_height= self.frame_width, self.frame_height
        self.singleframe= np.zeros((int(self.singleframe_height), int(self.singleframe_width),3),np.uint8)
        cv2.putText(self.singleframe, '2',(10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)
        result = Image.fromarray(self.singleframe)
        result = ImageTk.PhotoImage(result)
        self.panel_singleframe = Tkinter.Label(self.root , image = result)
        self.panel_singleframe.image = result
        self.panel_singleframe.place(x=self.panel.winfo_x(), y= self.panel.winfo_y()+ self.panel.winfo_height())
        self.root.update()

        # ==================================================
        #  Camera & Arduino Connection
        # ==================================================
        self.ArdMntr= MonitorThread()
        self.ArdMntr.start()

        self.CamMntr= CameraLink(self.CameraID)
        #self.CamMntr.connect_camera()

        # ==================================================
        #  Green Plant Indetifier
        # ==================================================
        self.plantsArea = PlantIdentifier()



        # ==================================================
        #  UI callback setting
        # ==================================================
        self.panel.after(50, self.check_frame_update)
        self.lbl_CurrPos.after(5, self.UI_callback)
        self.lbl_Soil_Data.after(5, self.Soil_callback)
        self.statuslabel.after(5, self.check_status)
        self.panel_mergeframe.bind('<Button-1>',self.mouse_LeftClick)
        self.root.bind('<F1>',self.rdbtn_MvAmount_click)
        self.root.bind('<F2>',self.rdbtn_MvAmount_click)
        self.root.bind('<F3>',self.rdbtn_MvAmount_click)
        self.root.bind('<F4>',self.rdbtn_MvAmount_click)
        self.root.bind('<F5>',self.rdbtn_MvAmount_click)
        #self.root.bind('<Up>',self.btn_MoveUp_click)
        self.root.bind('<Up>',self.btn_MoveAmount_click)
        self.root.bind('<Down>',self.btn_MoveAmount_click)
        self.root.bind('<Left>',self.btn_MoveAmount_click)
        self.root.bind('<Right>',self.btn_MoveAmount_click)
        self.root.bind('<Control-Up>',self.btn_MoveAmountZaxis_click)
        self.root.bind('<Control-Down>',self.btn_MoveAmountZaxis_click)




        # ====== Override CLOSE function ==============
        self.root.protocol('WM_DELETE_WINDOW',self.on_exit)

        # ==================================================
        #   Thread
        # ==================================================
        self.main_run_judge= True
        self.thread_main= class_MyThread.Thread(self.main_run)
        self.thread_main.start()

        self.scanning_judge= True
        #self.thread_scanning= threading.Thread(target= self.scanning_run)
        #self.thread_scanning= class_MyThread.Thread(self.scanning_run)
        #self.thread_scanning.start()

        if self.ArdMntr.connect:
            self.ArdMntr.set_MaxSpeed(self.MaxSpeed[0],'x')
            self.ArdMntr.set_MaxSpeed(self.MaxSpeed[1],'y')
            self.ArdMntr.set_MaxSpeed(self.MaxSpeed[2],'z')
            self.ArdMntr.set_Acceleration(self.Acceleration[0],'x')
            self.ArdMntr.set_Acceleration(self.Acceleration[1],'y')
            self.ArdMntr.set_Acceleration(self.Acceleration[2],'z')




    def rdbtn_PlantINdex_click(self):
        pass
    def rdbtn_BinaryMethodIndex_click(self):
        print 'BinaryMethodIndex: ',self.BinaryMethodIndex.get()
        if self.BinaryMethodIndex.get()==0:
            self.scale_threshold_graylevel.config(state= 'normal', label='Gray_level', fg='black')
        else:
            self.scale_threshold_graylevel.config(state= 'disabled', label='Gray_level (Disable)', fg= 'gray')

    def detectGreenPlant(self):
        self.plantsArea.setimage(self.singleframe)
        if self.PlantIndex.get()==0:
            _, image_plantIndex,_= self.plantsArea.LABimage(True)
        elif self.PlantIndex.get()==1:
            image_plantIndex= self.plantsArea.NDIimage(True)
        elif self.PlantIndex.get()==2:
            image_plantIndex= self.plantsArea.ExGimage(True)

        self.threshold_graylevel= self.scale_threshold_graylevel.get()
        image_plantIndex_thr= imgProcess_tool.binarialization(image_plantIndex.astype(np.uint8), self.BinaryMethodIndex.get(), self.threshold_graylevel)
        cv2.imwrite('Debug/img_thr.jpg',image_plantIndex_thr)

        self.threshold_MinSize, self.threshold_MaxSize=int(self.scale_threshold_MinSize.get()), int(self.scale_threshold_MaxSize.get())
        result= imgProcess_tool.findContours(image_plantIndex_thr, self.plantsArea.image_raw, (self.threshold_MinSize, self.threshold_MaxSize),True)
        #self.singleframe= result_ExG
        self.display_panel_singleframe(result)
        self.set_mergeframe_size(2,2)
        self.reset_mergeframe()
        self.display_panel_mergeframe(self.singleframe.copy(), 0, 0)
        self.display_panel_mergeframe(image_plantIndex.astype(np.uint8), 1, 0)
        self.display_panel_mergeframe(image_plantIndex_thr, 0, 1)
        self.display_panel_mergeframe(result, 1, 1)
        self.saveTimeIndex= datetime.now().strftime('%Y%m%d%H%M%S')
        self.readmergeframeIndex= gui_vars.rdbox_PlantIndexItem[self.PlantIndex.get()]

        print '=== ', gui_vars.saveImageProccesPath, self.readmergeframeIndex+'_'+self.saveTimeIndex
        self.saveImg_function(self.singleframe, gui_vars.saveImageProccesPath, self.readmergeframeIndex+'_'+self.saveTimeIndex+'_0_0')
        self.saveImg_function(image_plantIndex.astype(np.uint8), gui_vars.saveImageProccesPath, self.readmergeframeIndex+'_'+self.saveTimeIndex+'_0_1')
        self.saveImg_function(image_plantIndex_thr, gui_vars.saveImageProccesPath, self.readmergeframeIndex+'_'+self.saveTimeIndex+'_1_0')
        self.saveImg_function(result, gui_vars.saveImageProccesPath, self.readmergeframeIndex+'_'+self.saveTimeIndex+'_1_1')
        self.checkmouse_panel_mergeframe= True
        pass

    def method_OtsuBinary(self):
        print 'Start Otsu Binary.... '
        '''
        self.imageProcessor.set_threshold_size(int(self.scale_threshold_MinSize.get()))
        self.imageProcessor.set_threshold_graylevel(int(self.scale_threshold_graylevel.get()))
        result= self.imageProcessor.get_contour(self.singleframe, True, gui_vars.savePath, 'Otsu_Binary_'+self.imagename, 1)
        '''

        self.threshold_MaxSize= int(self.scale_threshold_MaxSize.get())
        img_thr= imgProcess_tool.binarialization(self.singleframe, 1)
        result= imgProcess_tool.findContours(img_thr, self.singleframe, [0,self.threshold_MaxSize] )
        self.display_panel_singleframe(result)


    # ====== DATABASE PLANT FUNCTION ==============
    def Database(self):
        global conn, cursor
        conn = sqlite3.connect("Database_Plant.db")
        cursor = conn.cursor()
        cursor.execute(
        "CREATE TABLE IF NOT EXISTS 'Plant_Database' (No INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,Name_Plant VARCHAR(100), Location_Plant_X INTEGER, Location_Plant_Y INTEGER, Date_Plant TIME, Amount_Water INTEGER, Age_Plant REAL)")
        conn.commit()

    def DatabaseAdd(self):
    	db = sqlite3.connect('Database_Plant.db')
    	db.execute("insert into Plant_Database (Name_Plant, Location_Plant_X, Location_Plant_Y, Date_Plant, Amount_Water, Age_Plant) values (?,?,?,datetime('now', 'localtime'),0,0)",
                    [NAME_PLANT.get(),LOCATION_PLANT_X.get(), LOCATION_PLANT_Y.get()])
    	db.commit()

    def Viewall(self):
        global tree
        self.Database()
        ViewFrame = Toplevel()
        ViewFrame.title("Database Plant")
        tes = str(datetime.datetime.now())
        #cursor.execute("UPDATE Plant_Database SET Age_Plant = (SELECT strftime('%s', 'now') - strftime('%s',Date_Plant) FROM Plant_Database)")
        #cursor.execute("SELECT * FROM 'Plant_Database'")
        cursor.execute("SELECT No, Name_Plant, Location_Plant_X, Location_Plant_Y, Date_Plant, Amount_Water, round(CAST((julianday('now','localtime') - julianday(Date_Plant))*24 AS real),2) AS Age_Plant FROM Plant_Database")
        fetch = cursor.fetchall()
        scrollbarx = Scrollbar(ViewFrame, orient=HORIZONTAL)
        scrollbary = Scrollbar(ViewFrame, orient=VERTICAL)
        tree = ttk.Treeview(ViewFrame, columns=("No", "Name_Plant", "Location_Plant_X", "Location_Plant_Y", "Date_Plant", "Amount_Water", "Age_Plant"),
                            selectmode=EXTENDED, yscrollcommand=scrollbary.set, xscrollcommand=scrollbarx.set)

        scrollbary.config(command=tree.yview)
        scrollbary.pack(side=RIGHT, fill=Y)
        scrollbarx.config(command=tree.xview)
        scrollbarx.pack(side=BOTTOM, fill=X)
        tree.heading('No', text="No", anchor=CENTER),
        tree.heading('Name_Plant', text="Name Plant", anchor=CENTER),
        tree.heading('Location_Plant_X', text="X", anchor=CENTER),
        tree.heading('Location_Plant_Y', text="Y", anchor=CENTER),
        tree.heading('Date_Plant', text="Date Plant", anchor=CENTER),
        tree.heading('Amount_Water', text="Amount Water", anchor=CENTER),
        tree.heading('Age_Plant', text="Age", anchor=CENTER),
        tree.column('#0', stretch=NO, minwidth=0, width=0),
        tree.column('#1', stretch=NO, minwidth=0, width=30),
        tree.column('#2', stretch=NO, minwidth=0, width=120),
        tree.column('#3', stretch=NO, minwidth=0, width=50),
        tree.column('#4', stretch=NO, minwidth=0, width=50),
        tree.column('#5', stretch=NO, minwidth=0, width=150),
        tree.column('#6', stretch=NO, minwidth=0, width=60),
        tree.column('#7', stretch=NO, minwidth=0, width=60)
        tree.pack()

        for data in fetch:
            tree.insert('', 'end', values=data)

        cursor.close()
        conn.close()

    def Update_data(self):
    	db = sqlite3.connect('Database_Plant.db')
    	db.execute('update Plant_Database set Name_Plant, Location_Plant_X, Location_Plant_Y) values (?,?,?,?)',
                    [NAME_PLANT.get(),LOCATION_PLANT_X.get(), LOCATION_PLANT_Y.get()])
    	db.commit()

    def Delete_data(self):
    	db = sqlite3.connect('Database_Plant.db')
    	db.execute('delete from Plant_Database where Name_Plant = ?',(NAME_PLANT.get(),))
    	db.commit()


    def store_para(self, arg_filepath, arg_filename):
        saveDict={}
        saveDict['thrshd_gray']= self.scale_threshold_graylevel.get()
        saveDict['thrshd_Minsize']= self.scale_threshold_MinSize.get()
        saveDict['thrshd_Maxsize']= self.scale_threshold_MaxSize.get()
        saveDict['Scan_X (Beg,Interval,Amount)']= [int(self.entry_1stXpos.get()), int(self.entry_ScanInterval_X.get()), int(self.entry_ScanAmount_X.get())]
        saveDict['Scan_Y (Beg,Interval,Amount)']= [int(self.entry_1stYpos.get()), int(self.entry_ScanInterval_Y.get()), int(self.entry_ScanAmount_Y.get())]
        saveDict['limit Maximum (X,Y)']= self.limit
        saveDict['Max Speed (X, Y)']= self.MaxSpeed
        saveDict['Ac/Deceleration (X, Y)']= self.Acceleration
        saveDict['Camera ID']= self.CameraID
        saveDict['Peripheral Setting']= self.Peripheral_para
        saveDict['Move Amount type (5 types)']= self.rdbtnMvAmount_Mode
        saveDict['script Path']= self.scriptPath
        self.config.write_json(saveDict)
        print "Para set"


    def run_schedule_1(self):
        self.btn_Schedule_Go.config(text= 'STOP',command=self.stop_schedule_1, fg='white', activeforeground= 'white', bg= self.bgRed,activebackground= self.bgRed_active)
        self.get_Time_1= self.entry_Time.get()
        self.get_Repeat_1= tkvar12.get()
        self.another_schedule_1 = ContinuousScheduler()
        if self.get_Repeat_1 == 'Every Day':
            self.another_schedule_1.every().day.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Every Hour':
            self.another_schedule_1.every().hour.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Monday':
            self.another_schedule_1.every().monday.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Tuesday':
            self.another_schedule_1.every().tuesday.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Wednesday':
            self.another_schedule_1.every().wednesday.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Thursday':
            self.another_schedule_1.every().thursday.at(self.get_Time_1).do(self.schedule_1)
        if self.get_Repeat_1 == 'Friday':
            self.another_schedule_1.every().friday.at(self.get_Time_1).do(self.schedule_1)
        else:
            self.get_Repeat_1 == 'Saturday'
            self.another_schedule_1.every().saturday.at(self.get_Time_1).do(self.schedule_1)

        self.halt_schedule_flag_1 = self.another_schedule_1.run_continuously()



    def run_schedule_2(self):
        self.btn_Schedule_Go_2.config(text= 'STOP',command=self.stop_schedule_2 ,fg='white', activeforeground= 'white', bg= self.bgRed,activebackground= self.bgRed_active)
        self.get_Time_2= self.entry_Time_2.get()
        self.get_Repeat_2= tkvar22.get()
        self.another_schedule_2 = ContinuousScheduler()
        if self.get_Repeat_2 == 'Every Day':
            self.another_schedule_2.every().day.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Every Hour':
            self.another_schedule_2.every().hour.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Monday':
            self.another_schedule_2.every().monday.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Tuesday':
            self.another_schedule_2.every().tuesday.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Wednesday':
            self.another_schedule_2.every().wednesday.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Thursday':
            self.another_schedule_2.every().thursday.at(self.get_Time_2).do(self.schedule_2)
        if self.get_Repeat_2 == 'Friday':
            self.another_schedule_2.every().friday.at(self.get_Time_2).do(self.schedule_2)
        else:
            self.get_Repeat_2 == 'Saturday'
            self.another_schedule_2.every().saturday.at(self.get_Time_2).do(self.schedule_2)

        self.halt_schedule_flag_2 = self.another_schedule_2.run_continuously()



    def run_schedule_3(self):
        self.btn_Schedule_Go_3.config(text= 'STOP', fg='white',command= self.stop_schedule_3, activeforeground= 'white', bg= self.bgRed,activebackground= self.bgRed_active)
        self.get_Time_3= self.entry_Time_3.get()
        self.get_Repeat_3= tkvar32.get()
        self.another_schedule_3 = ContinuousScheduler()
        if self.get_Repeat_3 == 'Every Day':
            self.another_schedule_3.every().day.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Every Hour':
            self.another_schedule_3.every().hour.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Monday':
            self.another_schedule_3.every().monday.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Tuesday':
            self.another_schedule_3.every().tuesday.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Wednesday':
            self.another_schedule_3.every().wednesday.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Thursday':
            self.another_schedule_3.every().thursday.at(self.get_Time_3).do(self.schedule_3)
        if self.get_Repeat_3 == 'Friday':
            self.another_schedule_3.every().friday.at(self.get_Time_3).do(self.schedule_3)
        else:
            self.get_Repeat_3 == 'Saturday'
            self.another_schedule_3.every().saturday.at(self.get_Time_3).do(self.schedule_3)

        self.halt_schedule_flag_3 = self.another_schedule_3.run_continuously()

    def stop_schedule_1(self):
        self.btn_Schedule_Go.config(text= 'Go',command=self.run_schedule_1 ,fg='white', activeforeground= 'white', bg= self.bgGreen,activebackground= self.bgGreen_active)
        self.halt_schedule_flag_1.set()

    def stop_schedule_2(self):
        self.btn_Schedule_Go_2.config(text= 'Go', command= self.run_schedule_2, fg='white', activeforeground= 'white', bg= self.bgGreen,activebackground= self.bgGreen_active)
        self.halt_schedule_flag_2.set()

    def stop_schedule_3(self):
        self.btn_Schedule_Go_3.config(text= 'Go', command= self.run_schedule_3, fg='white', activeforeground= 'white', bg= self.bgGreen,activebackground= self.bgGreen_active)
        self.halt_schedule_flag_3.set()

    def schedule_1(self):
        self.num_schedule = 1
        self.job_that_executes_once
        print('Schedule 1')

    def schedule_2(self):
        self.num_schedule = 2
        self.job_that_executes_once
        print('Schedule 2')

    def schedule_3(self):
        self.num_schedule = 3
        self.job_that_executes_once
        print('Schedule_3')

    def job_that_executes_once(self):
        # Do some work ...
        #print("I'm only going to run once!")
        if self.ArdMntr.connect:
            try:
                #X_home = 0
                #Y_home = 0
                #Z_home = 0
                #X_Target= int(self.entry_X_Schedule.get())
                #Y_Target= int(self.entry_Y_Schedule.get())
                #Z_Target= int(self.entry_Z_Schedule.get())
                if self.num_schedule == 1:
                    self.get_Action = tkvar11.get()
                    self.get_X_Pos = self.entry_X_Schedule.get()
                    self.get_Y_Pos = self.entry_Y_Schedule.get()
                    self.get_amount_water = int(self.entry_water_amount.get())
                if self.num_schedule == 2:
                    self.get_Action = tkvar12.get()
                    self.get_X_Pos = self.entry_X_Schedule_2.get()
                    self.get_Y_Pos = self.entry_Y_Schedule_2.get()
                    self.get_amount_water = int(self.entry_water_amount_2.get())
                else:
                    self.num_schedule == 3
                    self.get_Action = tkvar31.get()
                    self.get_X_Pos  = self.entry_X_Schedule_3.get()
                    self.get_Y_Pos  = self.entry_Y_Schedule_3.get()
                    self.get_amount_water = int(self.entry_water_amount_3.get())


                if self.get_Action == 'Watering' :
                    #for Watering 1 Location
                    '''if (X_Target>=0) & (X_Target<=self.limit[0]) & (Y_Target>=0) & (Y_Target<=self.limit[1]):
                        cmd= 'G00 X{0} Y{1} Z{2}'.format(X_Target, Y_Target, Z_Target)
                        #self.ArdMntr.serial_send(cmd)
                        print 'ArdMntr.move_Coord...'
                        self.ArdMntr.move_Coord(X_Target, Y_Target, Z_Target)
                        print 'Command: ',cmd
                        self.ArdMntr.Water_Schedule(self.pinNumb_water, not(self.ArdMntr.WaterOn) , 5)

                        time.sleep(1)
                    else:
                        tkMessageBox.showerror("Error", "The range of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1]))'''
                    if self.Start_Watering_judge:
                        #===================================
                        # Delete Scanning Thread
                        #===================================
                        self.Start_Watering_judge= False
                        del(self.thread_watering)

                    else:
                        self.input_Zpos= int(self.entry_Zpos.get())
                        print 'Start Watering'
                        try:
                            self.scan_X= [int(self.entry_1stXpos.get()), int(self.get_X_pos), int(self.entry_ScanAmount_X.get())]
                            self.scan_Y= [int(self.entry_1stYpos.get()), int(self.get_Y_Pos), int(self.entry_ScanAmount_Y.get())]
                            #print '### ', self.scan_X, self.scan_Y

                            self.ArdMntr.move_Coord(self.scan_X[0], self.scan_Y[0], self.input_Zpos)
                            if self.scan_X[0]+self.scan_X[1]*self.scan_X[2]<self.limit[0] | self.scan_Y[0]+self.scan_Y[1]*self.scan_Y[2]<self.limit[1]:
                                self.StartScan_judge= True

                                #=================================
                                # New Thread of Watering process
                                #================================
                                self.thread_watering= threading.Thread(target= self.watering_run)
                                self.thread_watering.start()
                                print '*** Watering...'
                                self.Lock_tabcontrol(True)
                                self.Lock_Menubar(True)
                                self.tabbox.tab(self.tab_loadscript, state='disable')

                            else:
                                tkMessageBox.showerror("Error", "The scanning of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1]))
                        except:
                            tkMessageBox.showerror('Error', 'Please enter nubmer')



                else :
                    #For Seeding
                    '''if (X_Target>=0) & (X_Target<=self.limit[0]) & (Y_Target>=0) & (Y_Target<=self.limit[1]):
                        cmd1= 'G00 X{0} Y{1} Z{2}'.format(X_Target, Y_Target, Z_Target)
                        #self.ArdMntr.serial_send(cmd)
                        print 'ArdMntr.move_Coord...'
                        self.ArdMntr.move_Coord(X_Target, Y_Target, Z_Target)
                        print 'Command: ',cmd1
                        self.ArdMntr.Seed_Schedule(self.pinNumb_seed, not(self.ArdMntr.SeedOn), 20)
                        print 'ArdMntr.move_Coord...'
                        cmd2= 'G00 X{0} Y{0} Z{0}'.format(X_home, Y_home, Z_home)
                        self.ArdMntr.move_Coord(X_home, Y_home, Z_home)
                        print 'Command: ',cmd2
                        time.sleep(1)
                    else:
                        tkMessageBox.showerror("Error", "The range of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1])) '''
                    #For scanning
                    if self.ArdMntr.connect:
                        try:
                            self.reset_mergeframe()
                            self.scan_X= [int(self.entry_1stXpos.get()), int(self.entry_ScanInterval_X.get()), int(self.entry_ScanAmount_X.get())]
                            self.scan_Y= [int(self.entry_1stYpos.get()), int(self.entry_ScanInterval_Y.get()), int(self.entry_ScanAmount_Y.get())]

                            self.set_mergeframe_size(self.scan_X[2], self.scan_Y[2])
                            self.reset_mergeframe()
                            #print '### ', self.scan_X, self.scan_Y

                            self.ArdMntr.move_Coord(self.scan_X[0], self.scan_Y[0], self.input_Zpos)
                            if self.scan_X[0]+self.scan_X[1]*self.scan_X[2]<self.limit[0] | self.scan_Y[0]+self.scan_Y[1]*self.scan_Y[2]<self.limit[1]:
                                self.StartScan_judge= True

                                #self.saveTimeIndex= datetime.now().strftime("%Y%m%d%H%M%S")
                                self.saveTimeIndex= datetime.now().strftime('%Y%m%d%H%M%S')

                                #=================================
                                # New Thread of Scanning process
                                #================================
                                self.thread_scanning= threading.Thread(target= self.scanning_run)
                                self.thread_scanning.start()

                                print '*** scanning...'
                                self.Lock_tabcontrol(True)
                                self.Lock_Menubar(True)

                                self.tabbox.tab(self.tab_loadscript, state='disable')


                                self.btn_StartScan.config(text= 'Stop Scan', fg='white', activeforeground= 'white', bg= self.bgRed, activebackground= self.bgRed_active)
                                self.root.update()
                            else:
                                tkMessageBox.showerror("Error", "The scanning of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1]))
                        except:
                            tkMessageBox.showerror('Error', 'Please enter nubmer')
                    else:
                        tkMessageBox.showerror("Error", "Arduino connection refused!")

            except:
                tkMessageBox.showerror("Error", "Please enter number!")

        else:
            tkMessageBox.showerror("Error", "Arduino connection refused!")

    # Override CLOSE function
    def on_exit(self):
        #When you click to exit, this function is called
        if tkMessageBox.askyesno("Exit", "Do you want to quit the application?"):
            #B self.store_para(gui_vars.saveParaPath, gui_vars.configName)
            print 'Close Main Thread...'
            self.main_run_judge= False
            self.ArdMntr.exit= True
            self.scanning_judge= False
            #self.CamMntr.stop_clean_buffer()
            #del(self.thread_main)
            self.thread_main.exit()
            print 'Close Arduino Thread...'
            #del(self.CamMntr.thread_clean_buffer)
            #print 'Close Scanning Thread...'
            #del(self.thread_scanning)
            print self.MaxSpeed

            self.CamMntr.release_cap()
            self.root.destroy()
#Make Grid
    def grid(result, line_distance):
        # vertical lines at an interval of "line_distance" pixel
        for x in range(line_distance,self.frame_width,line_distance):
            canvas.create_line(x, 0, x, self.frame_height, fill="#ffffff") #white color #ffffff
        # horizontal lines at an interval of "line_distance" pixel
        for y in range(line_distance, self.frame_height,line_distance):
            canvas.create_line(0, y, self.frame_width, y, fill="#ffffff") #white color #ffffff

    #Current Location Motor
    def UI_callback(self):
        if self.ArdMntr.connect== True:
            tmp_text= 'Location: (X, Y, Z)= ('+self.ArdMntr.cmd_state.strCurX+', '+self.ArdMntr.cmd_state.strCurY+', '+self.ArdMntr.cmd_state.strCurZ+')'
            #Soil_Data = self.ArdMntr.cmd_state.strSoil
        else:
            tmp_text='Arduino Connection Refuesed!'
            #Soil_Data = 'Get Soil Data Fail'
        self.lbl_CurrPos.config(text= tmp_text)
        self.lbl_CurrPos.after(10,self.UI_callback)

    def Soil_callback(self):
        if self.ArdMntr.connect== True:
            Soil_Data = self.ArdMntr.cmd_state.strSoil
        else:
            Soil_Data = 'Get Soil Data Fail'
        self.lbl_Soil_Data.config(text= Soil_Data)
        self.lbl_Soil_Data.after(10, self.Soil_callback)



    def IconResize(self, arg_readPath, arg_zoom= 1, arg_subsample= 4):
        photo_resize= PhotoImage(file= arg_readPath)
        photo_resize= photo_resize.zoom(arg_zoom)
        photo_resize= photo_resize.subsample(arg_subsample)
        return photo_resize

    def mouse_LeftClick(self, event):
        if self.checkmouse_panel_mergeframe:
            mouse_x, mouse_y= event.x, event.y
            #print '>> mouse(X,Y): ',mouse_x, mouse_y
            #print '>> split(X,Y): ', self.mergeframe_splitX, self.mergeframe_splitY

            begX = gui_vars.interval_x
            begY = self.mergeframe_spaceY
            tmp_X, tmp_Y= int((mouse_x - begX) / self.mergeframe_splitX), int((mouse_y - begY) / self.mergeframe_splitY)
            #print '>> RANGE(X, Y): ', begY + self.mergeframe_splitY * self.scan_Y[2], begX + self.mergeframe_splitX * self.scan_X[2]
            if begX < mouse_x < begX + self.mergeframe_splitX * self.scan_Y[2] and begY < mouse_y < begY + self.mergeframe_splitY * self.scan_X[2]:
                #print 'tmp_X, tmp_Y= ', tmp_X, ', ', tmp_Y  #2018.02.12

                if self.readmergeframeIndex == gui_vars.scanIndex:
                    readPath = gui_vars.saveScanningPath
                    #tmp_filename= '{0}_{1}'.format(tmp_Y * self.scan_X[1], tmp_X * self.scan_Y[1])
                    tmp_filename= '{0}_{1}'.format((self.scan_X[2] - 1 - tmp_Y) * self.scan_X[1], tmp_X * self.scan_Y[1])   #2018.02.12
                else:
                    readPath = gui_vars.saveImageProccesPath
                    #tmp_filename= '{0}_{1}'.format(tmp_Y, tmp_X)
                    tmp_filename= '{0}_{1}'.format(self.scan_X[2] - 1 - tmp_Y, tmp_X)   #2018.02.12

                #print 'click file: ', tmp_filename

                tmp_frame = utils_tool.readImage(readPath + self.readmergeframeIndex + '_' + self.saveTimeIndex + '_' + tmp_filename + '.jpg')
                if tmp_frame is not False:
                    self.imagename= self.readmergeframeIndex + '_' + self.saveTimeIndex + tmp_filename
                    self.singleframe= tmp_frame.copy()
                    self.display_panel_singleframe(tmp_frame)

                    mergeframe_canvas= self.mergeframe.copy()
                    cv2.rectangle(mergeframe_canvas ,(begX+self.mergeframe_splitX*tmp_X,begY+self.mergeframe_splitY*tmp_Y),(begX+self.mergeframe_splitX*(tmp_X+1), begY+self.mergeframe_splitY*(tmp_Y+1)),(0,255,100),2 )
                    result = Image.fromarray(mergeframe_canvas)
                    result = ImageTk.PhotoImage(result)
                    self.panel_mergeframe.configure(image = result)
                    self.panel_mergeframe.image = result


    def check_status(self):
        self.statuslabel.config(text= self.strStatus)
        self.statuslabel.after(10,self.check_status)

    def Lock_Menubar(self, arg_Lock):
        if arg_Lock:
            self.menubar.entryconfig('File', state='disabled')
            self.menubar.entryconfig('Setting', state='disabled')
            self.menubar.entryconfig('Communication', state='disabled')
            self.checkmouse_panel_mergeframe= False
        else:
            self.menubar.entryconfig('File', state='normal')
            self.menubar.entryconfig('Setting', state='normal')
            self.menubar.entryconfig('Communication', state='normal')
            self.checkmouse_panel_mergeframe= True

    def Lock_tabcontrol(self, arg_Lock):
        if arg_Lock:
            self.btn_MoveTo.config(state= 'disabled')
            self.entry_Xpos.config(state= 'disabled')
            self.entry_Ypos.config(state= 'disabled')
            self.entry_Zpos.config(state= 'disabled')
            self.btn_detect.config(state= 'disabled')
            self.btn_saveImg.config(state= 'disabled')
            self.entry_1stXpos.config(state= 'disabled')
            self.entry_1stYpos.config(state= 'disabled')
            self.entry_ScanInterval_X.config(state= 'disabled')
            self.entry_ScanInterval_Y.config(state= 'disabled')
            self.entry_ScanAmount_X.config(state= 'disabled')
            self.entry_ScanAmount_Y.config(state= 'disabled')
            self.checkmouse_panel_mergeframe= False
            self.btn_MoveUp.config(state= 'disabled')
            self.btn_MoveDown.config(state= 'disabled')
            self.btn_MoveLeft.config(state= 'disabled')
            self.btn_MoveRight.config(state= 'disabled')
            self.btn_MoveZUp.config(state= 'disabled')
            self.btn_MoveZDown.config(state= 'disabled')
            self.btn_Water.config(state= 'disabled')
            self.btn_Seed.config(state= 'disabled')
            self.btn_CamGrab.config(state= 'disabled')
        else:
            self.btn_MoveTo.config(state= 'normal')
            self.entry_Xpos.config(state= 'normal')
            self.entry_Ypos.config(state= 'normal')
            self.entry_Zpos.config(state= 'normal')
            self.btn_detect.config(state= 'normal')
            self.btn_saveImg.config(state= 'normal')
            self.entry_1stXpos.config(state= 'normal')
            self.entry_1stYpos.config(state= 'normal')
            self.entry_ScanInterval_X.config(state= 'normal')
            self.entry_ScanInterval_Y.config(state= 'normal')
            self.entry_ScanAmount_X.config(state= 'normal')
            self.entry_ScanAmount_Y.config(state= 'normal')
            self.checkmouse_panel_mergeframe= True
            self.btn_MoveUp.config(state= 'normal')
            self.btn_MoveDown.config(state= 'normal')
            self.btn_MoveLeft.config(state= 'normal')
            self.btn_MoveRight.config(state= 'normal')
            self.btn_MoveZUp.config(state= 'normal')
            self.btn_MoveZDown.config(state= 'normal')
            self.btn_Water.config(state= 'normal')
            self.btn_Seed.config(state= 'normal')
            self.btn_CamGrab.config(state= 'normal')

    def Lock_tabloadscript(self, arg_Lock):
        if arg_Lock:
            self.entry_scriptPath.config(state= 'disabled')
            self.btn_loadscript.config(state= 'disabled')
            self.btn_choosescript.config(state= 'disabled')
            self.btn_savescript.config(state= 'disabled')
            self.txtbox_script.configure(text_state= 'disabled')
        else:
            self.entry_scriptPath.config(state= 'normal')
            self.btn_loadscript.config(state= 'normal')
            self.btn_choosescript.config(state= 'normal')
            self.btn_savescript.config(state= 'normal')
            self.txtbox_script.configure(text_state= 'normal')



    def set_ArdConnect(self):
        self.ArdMntr.connect_serial()


    def set_CamConnect(self):
        cameraID= CameraConnection(self.root, self.CamMntr.camera_id)
        print '*** ',cameraID.result, ', ', self.CamMntr.camera_id
        if cameraID.result is not None and cameraID.result != self.CamMntr.camera_id:
            print 'Switch Camera ID'
            self.CamMntr.connect_camera(cameraID.result)
            self.CameraID= self.CamMntr.camera_id

    def set_Peripheral(self):
        #Var= PeripheralSetting(self.root, [('Fan',8),('Water Pump',9)])
        #print '>>> ',self.Peripheral_para
        Var= PeripheralSetting(self.root, self.Peripheral_para)
        if Var.result is not None:
            self.Peripheral_para= Var.result
        print '*** Return Value: ',Var.result

        #-2018.02.28-CGH
        for key, value in self.Peripheral_para:
            if key.strip().replace(' ','').lower() == 'waterpump':  # is -> == 2018.02.28
				self.pinNumb_water= value
				print 'pinNumb_water: ', self.pinNumb_water		#2018.02.28
            if key.strip().replace(' ','').lower() == 'vaccumpump':	# is -> == 2018.02.28
                self.pinNumb_seed= value
                print 'pinNumb_seed: ', self.pinNumb_seed		#2018.02.28
            if key.strip().replace(' ','').lower() == 'fan':		# is -> == 2018.02.28
				self.pinNumb_fan= value
				print 'pinNumb_fan: ', self.pinNumb_fan			#2018.02.28

    def set_Motor(self):
        if self.ArdMntr.connect:
            Var= MotorSetting(self.root, self.MaxSpeed, self.Acceleration)
            if Var.result is not None:
                print 'result: ',Var.result
                #self.MaxSpeed= [Var.result[0], Var.result[2]]
                #self.Acceleration= [Var.result[1], Var.result[3]]
                self.MaxSpeed= [Var.result[0], Var.result[2], Var.result[4]]
                self.Acceleration= [Var.result[1], Var.result[3], Var.result[5]]
                self.ArdMntr.set_MaxSpeed(self.MaxSpeed[0],'x')
                self.ArdMntr.set_MaxSpeed(self.MaxSpeed[1],'y')
                self.ArdMntr.set_MaxSpeed(self.MaxSpeed[2],'z')
                self.ArdMntr.set_Acceleration(self.Acceleration[0],'x')
                self.ArdMntr.set_Acceleration(self.Acceleration[1],'y')
                self.ArdMntr.set_Acceleration(self.Acceleration[2],'z')
            #self.ArdMntr.set_MaxSpeed()
        else:
            tkMessageBox.showerror("Error", "Arduino connection refused!\n Please check its connection.")

    def set_frame(self, frame):
        self.frame= frame

    def display_panel_singleframe(self, arg_frame):
        tmp_frame= cv2.cvtColor(arg_frame, cv2.COLOR_BGR2RGB)
        tmp_frame = self.mark_cross_line(tmp_frame)
        tmp_frame= cv2.resize(tmp_frame,(self.singleframe_width,self.singleframe_height),interpolation=cv2.INTER_LINEAR)	#2018.02.20-???
        result = Image.fromarray(tmp_frame)
        result = ImageTk.PhotoImage(result)
        self.panel_singleframe.configure(image = result)
        self.panel_singleframe.image = result

    def reset_mergeframe(self):
        self.mergeframe= np.zeros((int(self.mergeframe_height), int(self.mergeframe_width),3),np.uint8)
        cv2.putText(self.mergeframe, 'Display Scanning Result',(10,20),cv2.FONT_HERSHEY_SIMPLEX, 0.5,(255,255,255),1)
        cv2.putText(self.mergeframe, '0',(6,545),cv2.FONT_HERSHEY_SIMPLEX, 0.3,(255,255,255),1)
        # Axis Y
        cv2.putText(self.mergeframe, '86', (130,545),cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
        cv2.putText(self.mergeframe, '172', (254,545), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
        cv2.putText(self.mergeframe, '258', (378,545), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
        cv2.putText(self.mergeframe, '344', (502,545), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)
        cv2.putText(self.mergeframe, '430', (620,545), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255,255,255), 1)

        #Axis Y
        cv2.putText(self.mergeframe, '100', (0, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)
        cv2.putText(self.mergeframe, '200', (0, 375), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)
        cv2.putText(self.mergeframe, '300', (0, 295), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)
        cv2.putText(self.mergeframe, '400', (0, 215), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)
        cv2.putText(self.mergeframe, '500', (0, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)
        cv2.putText(self.mergeframe, '600', (0, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (255,255,255), 1)

    def set_mergeframe_size(self, arg_x, arg_y):
        self.mergeframe_splitX = int((self.mergeframe_width - gui_vars.interval_x*2) / arg_y)
        self.mergeframe_splitY = int((self.mergeframe_height - 100) / arg_x)

    def display_panel_mergeframe(self, arg_frame, arg_stepX, arg_stepY):
        print '*** ',len(arg_frame.shape)
        if len(arg_frame.shape)==3:
            tmp_frame= cv2.cvtColor(arg_frame, cv2.COLOR_BGR2RGB)
        else:
            tmp_frame= cv2.cvtColor(arg_frame, cv2.COLOR_GRAY2RGB)

        tmp_frame= cv2.resize(tmp_frame,(self.mergeframe_splitX,self.mergeframe_splitY),interpolation=cv2.INTER_LINEAR)
        begX= gui_vars.interval_x+self.mergeframe_splitX*arg_stepX
        begY= self.mergeframe_spaceY+ self.mergeframe_splitY* arg_stepY
        self.mergeframe[begY:begY+ self.mergeframe_splitY, begX: begX+ self.mergeframe_splitX]= tmp_frame
        #begY= self.mergeframe_height- 50- self.mergeframe_splitY*arg_stepY
        #self.mergeframe[begY-self.mergeframe_splitY:begY, begX: begX+ self.mergeframe_splitX]= tmp_frame
        self.mergeframe_stepX= arg_stepX
        self.mergeframe_stepY= arg_stepY
        print '>> mergeframe_splitY, splitX= ', self.mergeframe_splitY, ', ', self.mergeframe_splitX
        print '>> tmp_frame.shape[0,1]= ', tmp_frame.shape[0],', ',tmp_frame.shape[1]

        result = Image.fromarray(self.mergeframe)
        result = ImageTk.PhotoImage(result)
        self.panel_mergeframe.configure(image = result)
        self.panel_mergeframe.image = result

    def rdbtn_MvAmount_click(self, event= None):
        if event is not None:
            if event.keysym == 'F1':
                self.rdbtn_MvAmount_1.select()
            elif event.keysym == 'F2':
                self.rdbtn_MvAmount_5.select()
            elif event.keysym == 'F3':
                self.rdbtn_MvAmount_10.select()
            elif event.keysym == 'F4':
                self.rdbtn_MvAmount_20.select()
            elif event.keysym == 'F5':
                self.rdbtn_MvAmount_50.select()
        self.Move_interval= self.MvAmount.get()
        print 'rdVal',self.Move_interval


    def btn_MoveAmount_click(self, event= None):
        #print '*** ',self.tabbox.index(self.tabbox.select())
        #print '*** ',self.tabbox.select()
        if self.tabbox.index(self.tabbox.select())==0:
            if type(event) is types.StringType:
                move_type= event
            else:
                print'event.keysym ', event.keysym
                print 'event.keycode', event.keycode
                move_type= event.keysym
                print 'Test ',move_type is 'Up'
            #self.Move_interval= self.MvAmount.get()

            tmp_x, tmp_y, tmp_z= self.ArdMntr.get_CurPosition()
            print '==>>> ',tmp_x, tmp_y, tmp_z
            print '==>>> ',self.Move_interval * self.Move_intervalUnit
            if move_type == 'Up':
                After_MoveAmount_X1 = tmp_x + self.Move_interval
                self.ArdMntr.move_Coord(tmp_x + self.Move_interval * self.Move_intervalUnit, tmp_y, tmp_z)
                if self.Move_interval == 10 and (After_MoveAmount_X1 - self.Move_interval) == tmp_x :
                    Move_Amount10_Up = pd.DataFrame([['3', 'Move Amount X Axis (Up) 10mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['3'])
                    Move_Amount10_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=3, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Up = pd.DataFrame([['3', 'Move Amount X Axis (Up) 10mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['3'])
                    Move_Amount10_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=3, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_X1 - self.Move_interval) == tmp_x :
                    Move_Amount50_Up = pd.DataFrame([['4', 'Move Amount X Axis (Up) 50mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['4'])
                    Move_Amount50_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=4, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Up = pd.DataFrame([['4', 'Move Amount X Axis (Up) 50mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['4'])
                    Move_Amount50_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=4, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_X1 - self.Move_interval) == tmp_x :
                    Move_Amount100_Up = pd.DataFrame([['5', 'Move Amount X Axis (Up) 100mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['5'])
                    Move_Amount100_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=5, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Up = pd.DataFrame([['5', 'Move Amount X Axis (Up) 100mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['5'])
                    Move_Amount100_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=5, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_X1 - self.Move_interval) == tmp_x :
                    Move_Amount200_Up = pd.DataFrame([['6', 'Move Amount X Axis (Up) 200mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['6'])
                    Move_Amount200_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=6, startcol= 0)
                    writer.save()
                else:
                    Move_Amount200_Up = pd.DataFrame([['6', 'Move Amount X Axis (Up) 200mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['6'])
                    Move_Amount200_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=6, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_X1 - self.Move_interval) == tmp_x :
                    Move_Amount500_Up = pd.DataFrame([['7', 'Move Amount X Axis (Up) 500mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['7'])
                    Move_Amount500_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=7, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Up = pd.DataFrame([['7', 'Move Amount X Axis (Up) 500mm',  str(After_MoveAmount_X1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['7'])
                    Move_Amount500_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=7, startcol= 0)
                    writer.save()

            elif move_type == 'Down':
                self.ArdMntr.move_Coord(tmp_x - self.Move_interval * self.Move_intervalUnit, tmp_y, tmp_z)
                After_MoveAmount_X2 = tmp_x - self.Move_interval
                if self.Move_interval == 10 and (After_MoveAmount_X2 + self.Move_interval) == tmp_x :
                    Move_Amount10_Down = pd.DataFrame([['8', 'Move Amount X Axis (Down) 10mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['8'])
                    Move_Amount10_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=8, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Down = pd.DataFrame([['8', 'Move Amount X Axis (Down) 10mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['8'])
                    Move_Amount10_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=8, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_X2 + self.Move_interval) == tmp_x :
                    Move_Amount50_Down = pd.DataFrame([['9', 'Move Amount X Axis (Down) 50mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['9'])
                    Move_Amount50_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=9, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Down = pd.DataFrame([['9', 'Move Amount X Axis (Down) 50mm',  str(After_MoveAmount_X) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['9'])
                    Move_Amount50_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=9, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_X2 + self.Move_interval) == tmp_x :
                    Move_Amount100_Down = pd.DataFrame([['10', 'Move Amount X Axis (Down) 100mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['10'])
                    Move_Amount100_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=10, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Down = pd.DataFrame([['10', 'Move Amount X Axis (Down) 100mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['10'])
                    Move_Amount100_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=10, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_X2 + self.Move_interval) == tmp_x :
                    Move_Amount200_Down = pd.DataFrame([['11', 'Move Amount X Axis (Down) 200mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['11'])
                    Move_Amount200_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=11, startcol= 0)
                    writer.save()
                else:
                    Move_Amount200_Down = pd.DataFrame([['11', 'Move Amount X Axis (Down) 200mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['11'])
                    Move_Amount200_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=11, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_X2 + self.Move_interval) == tmp_x :
                    Move_Amount500_Down = pd.DataFrame([['12', 'Move Amount X Axis (Down) 500mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['12'])
                    Move_Amount500_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=12, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Down = pd.DataFrame([['12', 'Move Amount X Axis (Down) 500mm',  str(After_MoveAmount_X2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_x) + '(Start of Coordinates)' , str(After_MoveAmount_X2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['12'])
                    Move_Amount500_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=12, startcol= 0)
                    writer.save()

            elif move_type == 'Right':
                self.ArdMntr.move_Coord(tmp_x, tmp_y + self.Move_interval * self.Move_intervalUnit, tmp_z)
                After_MoveAmount_Y1 = tmp_y + self.Move_interval
                if self.Move_interval == 10 and (After_MoveAmount_Y1 - self.Move_interval) == tmp_y :
                    Move_Amount10_Right = pd.DataFrame([['13', 'Move Amount Y Axis (Right) 10mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['13'])
                    Move_Amount10_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=13, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Right = pd.DataFrame([['13', 'Move Amount Y Axis (Right) 10mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['13'])
                    Move_Amount10_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=13, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_Y1 - self.Move_interval) == tmp_y :
                    Move_Amount50_Right = pd.DataFrame([['14', 'Move Amount Y Axis (Right) 50mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['14'])
                    Move_Amount50_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=14, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Right= pd.DataFrame([['14', 'Move Amount Y Axis (Right) 50mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['14'])
                    Move_Amount50_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=14, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_Y1 - self.Move_interval) == tmp_y :
                    Move_Amount100_Right = pd.DataFrame([['15', 'Move Amount Y Axis (Right) 100mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['15'])
                    Move_Amount100_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=15, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Right = pd.DataFrame([['15', 'Move Amount Y Axis (Right) 100mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['15'])
                    Move_Amount100_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=15, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_Y1 - self.Move_interval) == tmp_y :
                    Move_Amount200_Right = pd.DataFrame([['16', 'Move Amount Y Axis (Right) 200mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['16'])
                    Move_Amount200_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=16, startcol= 0)
                    writer.save()
                else:
                    Move_Amount200_Right= pd.DataFrame([['16', 'Move Amount Y Axis (Right) 200mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['16'])
                    Move_Amount200_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=16, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_Y1 - self.Move_interval) == tmp_y :
                    Move_Amount500_Right= pd.DataFrame([['17', 'Move Amount Y Axis (Right) 500mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['17'])
                    Move_Amount500_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=17, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Right= pd.DataFrame([['17', 'Move Amount Y Axis (Right) 500mm',  str(After_MoveAmount_Y1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['17'])
                    Move_Amount500_Right.to_excel(writer,'Sheet1', index=False, header=False, startrow=17, startcol= 0)
                    writer.save()

            elif move_type == 'Left':
                self.ArdMntr.move_Coord(tmp_x, tmp_y - self.Move_interval * self.Move_intervalUnit, tmp_z)
                After_MoveAmount_Y2 = tmp_y - self.Move_interval
                if self.Move_interval == 10 and (After_MoveAmount_Y2 + self.Move_interval) == tmp_y :
                    Move_Amount10_Left = pd.DataFrame([['18', 'Move Amount Y Axis (Left) 10mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['18'])
                    Move_Amount10_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=18, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Left = pd.DataFrame([['18', 'Move Amount Y Axis (Left) 10mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['18'])
                    Move_Amount10_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=18, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_Y2 + self.Move_interval) == tmp_y :
                    Move_Amount50_Left = pd.DataFrame([['19', 'Move Amount Y Axis (Left) 50mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['19'])
                    Move_Amount50_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=19, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Left = pd.DataFrame([['19', 'Move Amount Y Axis (Left) 50mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['19'])
                    Move_Amount50_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=19, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_Y2 + self.Move_interval) == tmp_y :
                    Move_Amount100_Left = pd.DataFrame([['20', 'Move Amount Y Axis (Left) 100mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['20'])
                    Move_Amount100_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=20, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Left = pd.DataFrame([['20', 'Move Amount Y Axis (Left) 100mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['20'])
                    Move_Amount100_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=20, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_Y2 + self.Move_interval) == tmp_y :
                    Move_Amount200_Left = pd.DataFrame([['21', 'Move Amount Y Axis (Left) 200mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['21'])
                    Move_Amount200_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=21, startcol= 0)
                    writer.save()
                else:
                    Move_Amount200_Left = pd.DataFrame([['21', 'Move Amount Y Axis (Left) 200mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['21'])
                    Move_Amount200_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=21, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_Y2 + self.Move_interval) == tmp_y :
                    Move_Amount500_Left = pd.DataFrame([['22', 'Move Amount Y Axis (Left) 500mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['22'])
                    Move_Amount500_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=22, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Left = pd.DataFrame([['22', 'Move Amount Y Axis (Left) 500mm',  str(After_MoveAmount_Y2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_y) + '(Start of Coordinates)' , str(After_MoveAmount_Y2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['22'])
                    Move_Amount500_Left.to_excel(writer,'Sheet1', index=False, header=False, startrow=22, startcol= 0)
                    writer.save()

    def btn_MoveAmountZaxis_click(self, event= None):
        if self.tabbox.index(self.tabbox.select())==0:
            if type(event) is types.StringType:
                move_type= event
            else:
                move_type= event.keysym

            tmp_x, tmp_y, tmp_z= self.ArdMntr.get_CurPosition()
            if move_type == 'Up':
                After_MoveAmount_Z1 = tmp_z + self.Move_interval
                self.ArdMntr.move_Coord(tmp_x, tmp_y, tmp_z + self.Move_interval * self.Move_intervalUnit)
                if self.Move_interval == 10 and (After_MoveAmount_Z1 - self.Move_interval) == tmp_z :
                    Move_Amount10_Z_Up = pd.DataFrame([['23', 'Move Amount Z Axis (Up) 10mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['23'])
                    Move_Amount10_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=23, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Z_Up = pd.DataFrame([['23', 'Move Amount Z Axis (Up) 10mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['23'])
                    Move_Amount10_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=23, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_Z1 - self.Move_interval) == tmp_z :
                    Move_Amount50_Z_Up = pd.DataFrame([['24', 'Move Amount Z Axis (Up) 50mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['24'])
                    Move_Amount50_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=24, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Z_Up = pd.DataFrame([['24', 'Move Amount Z Axis (Up) 50mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['24'])
                    Move_Amount50_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=24, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_Z1 - self.Move_interval) == tmp_z :
                    Move_Amount100_Z_Up = pd.DataFrame([['25', 'Move Amount Z Axis (Up) 100mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['25'])
                    Move_Amount100_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=25, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Z_Up = pd.DataFrame([['25', 'Move Amount Z Axis (Up) 100mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['25'])
                    Move_Amount100_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=25, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_Z1 - self.Move_interval) == tmp_z :
                    Move_Amount200_Z_Up = pd.DataFrame([['26', 'Move Amount Z Axis (Up) 200mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['26'])
                    writer.save()
                    Move_Amount200_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=26, startcol= 0)
                else:
                    Move_Amount200_Z_Up = pd.DataFrame([['26', 'Move Amount Z Axis (Up) 200mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['26'])
                    Move_Amount200_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=26, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_Z1 - self.Move_interval) == tmp_z :
                    Move_Amount500_Z_Up = pd.DataFrame([['27', 'Move Amount Z Axis (Up) 500mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['27'])
                    Move_Amount500_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=27, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Z_Up = pd.DataFrame([['27', 'Move Amount Z Axis (Up) 500mm',  str(After_MoveAmount_Z1) + '(End of Coordinates)' + '-' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z1 - self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['27'])
                    Move_Amount500_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=27, startcol= 0)
                    writer.save()

            elif move_type == 'Down':
                self.ArdMntr.move_Coord(tmp_x, tmp_y, tmp_z - self.Move_interval * self.Move_intervalUnit)
                After_MoveAmount_Z2 = tmp_z  - self.Move_interval
                if self.Move_interval == 10 and (After_MoveAmount_Z2 + self.Move_interval) == tmp_z :
                    Move_Amount10_Z_Down = pd.DataFrame([['28', 'Move Amount Z Axis (Down) 10mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['28'])
                    Move_Amount10_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=28, startcol= 0)
                    writer.save()
                else:
                    Move_Amount10_Z_Down = pd.DataFrame([['28', 'Move Amount Z Axis (Down) 10mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['28'])
                    Move_Amount10_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=28, startcol= 0)
                    writer.save()

                if self.Move_interval == 50 and (After_MoveAmount_Z2 + self.Move_interval) == tmp_z :
                    Move_Amount50_Z_Down = pd.DataFrame([['29', 'Move Amount Z Axis (Down) 50mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['29'])
                    Move_Amount50_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=29, startcol= 0)
                    writer.save()
                else:
                    Move_Amount50_Z_Down = pd.DataFrame([['29', 'Move Amount Z Axis (Down) 50mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['29'])
                    Move_Amount50_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=29, startcol= 0)
                    writer.save()

                if self.Move_interval == 100 and (After_MoveAmount_Z2 + self.Move_interval) == tmp_z :
                    Move_Amount100_Z_Down = pd.DataFrame([['30', 'Move Amount Z Axis (Down) 100mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['30'])
                    Move_Amount100_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=30, startcol= 0)
                    writer.save()
                else:
                    Move_Amount100_Z_Down = pd.DataFrame([['30', 'Move Amount Z Axis (Down) 100mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['30'])
                    Move_Amount100_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=30, startcol= 0)
                    writer.save()

                if self.Move_interval == 200 and (After_MoveAmount_Z2 + self.Move_interval) == tmp_z :
                    Move_Amount200_Z_Down = pd.DataFrame([['31', 'Move Amount Z Axis (Down) 200mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['31'])
                    Move_Amount200_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=31, startcol= 0)
                    writer.save()
                else:
                    Move_Amount200_Z_Down = pd.DataFrame([['31', 'Move Amount Z Axis (Down) 200mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['31'])
                    Move_Amount200_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=31, startcol= 0)
                    writer.save()

                if self.Move_interval == 500 and (After_MoveAmount_Z2 + self.Move_interval) == tmp_z :
                    Move_Amount500_Z_Down = pd.DataFrame([['32', 'Move Amount Z Axis (Down) 500mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Success']], index=['32'])
                    Move_Amount500_Z_Down.to_excel(writer,'Sheet1', index=False, header=False, startrow=12, startcol= 0)
                    writer.save()
                else:
                    Move_Amount500_Z_Up = pd.DataFrame([['32', 'Move Amount Z Axis (Down) 500mm',  str(After_MoveAmount_Z2) + '(End of Coordinates)' + '+' + str(self.Move_interval) +'(Move Amount)' + '=' + str(tmp_z) + '(Start of Coordinates)' , str(After_MoveAmount_Z2 + self.Move_interval) + '(Start of Coordinates)' , 'Fail']], index=['32'])
                    Move_Amount500_Z_Up.to_excel(writer,'Sheet1', index=False, header=False, startrow=32, startcol= 0)
                    writer.save()

    def btn_Seed_click(self):
        if self.ArdMntr.connect:
            self.ArdMntr.switch_Seed(self.pinNumb_seed, not(self.ArdMntr.SeedOn))
            if self.ArdMntr.SeedOn:
                text_seed= 'On'
                SeedOn = '1'
                self.btn_Indi_Seed.config(text= text_seed, fg='white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen)
                self.root.update()
                Seed_Plant = pd.DataFrame([['34', 'Vaccum Pump On (Seed)', '1', SeedOn, 'Sucess']], index=['34'])
                Seed_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=34, startcol= 0)
                writer.save()

            else:
                text_seed= 'Off'
                SeedOff ='0'
                self.btn_Indi_Seed.config(text= text_seed, fg='white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed)
                self.root.update()
                Seed_Plant = pd.DataFrame([['34', 'Vaccum Pump On (Seed)' , '1', SeedOff, 'Failed']], index=['34'])
                Seed_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=34, startcol= 0)
                writer.save()
            print 'Seeding... '

    def btn_Water_click(self):
        if self.ArdMntr.connect:
            self.ArdMntr.switch_Water(self.pinNumb_water, not(self.ArdMntr.WaterOn) , -1)
            if self.ArdMntr.WaterOn:
                text_water= 'On'
                self.btn_Indi_Water.config(text= text_water, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen)
                self.root.update()
                WaterOn = '1'
                Water_Plant = pd.DataFrame([['35', 'Water Pump On (Water)', '1', WaterOn, 'Sucess']], index=['35'])
                Water_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=35, startcol= 0)
                writer.save()


            else:
                text_water= 'Off'
                self.btn_Indi_Water.config(text=text_water, fg= 'white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed)
                self.root.update()
                WaterOff = '0'
                Water_Plant = pd.DataFrame([['35', 'Water Pump On (Water)' , '1', WaterOff, 'Failed']], index=['35'])
                Water_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=35, startcol= 0)
                writer.save()
            print 'Watering... '

    def btn_Light_click(self):
        if self.ArdMntr.connect:
            self.ArdMntr.switch_Light(self.pinNumb_fan, not(self.ArdMntr.LightOn))
            if self.ArdMntr.LightOn:
                text_light= 'On'
                self.btn_Indi_Light.config(text= text_light, fg= 'white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen)
                self.root.update()
                LightOn = '1'
                LightOff = '0'
                if self.ArdMntr.LightOn :
                    Water_Plant = pd.DataFrame([['36', 'Light On', '1', LightOn, 'Sucess']], index=['36'])
                    Water_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=36, startcol= 0)
                    writer.save()
                else:
                    Water_Plant = pd.DataFrame([['36', 'Light On' , '1', LightOff, 'Failed']], index=['36'])
                    Water_Plant.to_excel(writer,'Sheet1', index=False, header=False, startrow=36, startcol= 0)
                    writer.save()
            else:
                text_light= 'Off'
                self.btn_Indi_Light.config(text=text_light, fg= 'white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed)
                self.root.update()
            print 'Lighting... '


    def btn_choosescript_click(self):
        str_scriptPath = tkFileDialog.askopenfilename(title = "Select file",filetypes = (("all files","*.*"),("Text File", "*.txt"),("jpeg files","*.jpg")))
        print '>>>> ', str_scriptPath
        if str_scriptPath !="":
            self.entry_scriptPath.delete(0,"end")
            self.entry_scriptPath.insert(Tkinter.END, str_scriptPath)
            self.scriptPath= str_scriptPath

    def btn_loadscript_click(self):
        #self.scriptPath= self.entry_scriptPath.get()
        tmpPath= self.entry_scriptPath.get()
        if utils_tool.check_file(tmpPath):
            #self.txtbox_script.delete('1.0', END)
            self.txtbox_script.clear()
            self.txtbox_script.importfile(tmpPath)
            self.txtbox_script.configure(label_text= "- "+ tmpPath.split("/")[-1]+" -")
        else:
            tkMessageBox.showerror("Error", "'%s' dost not exist !" % tmpPath)


    def btn_savescript_click(self):
        tmpPath= self.entry_scriptPath.get()
        self.txtbox_script.exportfile(tmpPath)

    def btn_runscript_click(self):
        if self.ArdMntr.connect:
            if self.StartRunScript_judge:
                #===================================
                # Delete Scanning Thread
                #===================================
                self.StartRunScript_judge= False
                del(self.thread_runningScript)

            else:

                self.txtbox_script.exportfile("tmp.txt")
                #=================================
                # New Thread of Scanning process
                #================================
                self.thread_runningScript= threading.Thread(target= self.runningScript_run)
                self.thread_runningScript.start()

                self.tabbox.tab(self.tab_control, state='disable')
                self.Lock_tabloadscript(True)
                self.btn_runscript.config(text= 'STOP', fg='white', activeforeground= 'white', bg= self.bgRed,activebackground= self.bgRed_active)
                self.StartRunScript_judge= True
        else:
            tkMessageBox.showerror("Error", "Arduino connection refused!")

    def btn_StartScan_click(self):
        #B self.imageProcessor.set_threshold_size(int(self.scale_threshold_MinSize.get()))
        #B self.imageProcessor.set_threshold_graylevel(int(self.scale_threshold_graylevel.get()))

        self.input_Zpos= int(self.entry_Zpos.get())
        self.readmergeframeIndex= gui_vars.scanIndex
        print 'Start'

        if self.StartScan_judge:
            #===================================
            # Delete Scanning Thread
            #===================================
            self.StartScan_judge= False
            del(self.thread_scanning)

        else:
            if self.ArdMntr.connect:
                try:
                    self.reset_mergeframe()
                    self.scan_X= [int(self.entry_1stXpos.get()), int(self.entry_ScanInterval_X.get()), int(self.entry_ScanAmount_X.get())]
                    self.scan_Y= [int(self.entry_1stYpos.get()), int(self.entry_ScanInterval_Y.get()), int(self.entry_ScanAmount_Y.get())]
                    self.set_mergeframe_size(self.scan_X[2], self.scan_Y[2])
                    self.reset_mergeframe()
                    #print '### ', self.scan_X, self.scan_Y

                    self.ArdMntr.move_Coord(self.scan_X[0], self.scan_Y[0], self.input_Zpos)
                    if self.scan_X[0]+self.scan_X[1]*self.scan_X[2]<self.limit[0] | self.scan_Y[0]+self.scan_Y[1]*self.scan_Y[2]<self.limit[1]:
                        self.StartScan_judge= True

                        #self.saveTimeIndex= datetime.now().strftime("%Y%m%d%H%M%S")
                        self.saveTimeIndex= datetime.now().strftime('%Y%m%d%H%M%S')

                        #=================================
                        # New Thread of Scanning process
                        #================================
                        self.thread_scanning= threading.Thread(target= self.scanning_run)
                        self.thread_scanning.start()

                        print '*** scanning...'
                    	self.Lock_tabcontrol(True)
                        self.Lock_Menubar(True)

                        self.tabbox.tab(self.tab_loadscript, state='disable')


                        self.btn_StartScan.config(text= 'Stop Scan', fg='white', activeforeground= 'white', bg= self.bgRed, activebackground= self.bgRed_active)
                        self.root.update()
                    else:
                        tkMessageBox.showerror("Error", "The scanning of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1]))
                except:
                    tkMessageBox.showerror('Error', 'Please enter nubmer')
            else:
                tkMessageBox.showerror("Error", "Arduino connection refused!")


    def btn_saveImg_click(self):
        #self.saveImg= True

        self.imagename= ''
        self.singleframe = self.CamMntr.get_frame()
        self.saveImg_function(self.singleframe, gui_vars.savePath, self.imagename)
        self.display_panel_singleframe(self.singleframe)

        tes_soil = 'T01 V1'
        self.ArdMntr.serial_send(tes_soil)
        time.sleep(10)
        soil_data = float(self.ArdMntr.cmd_state.strSoil)
        print('Tes')
        print(soil_data)
        self.lbl_Soil_Data.config(text= soil_data)

        if soil_data > 200 :
            print('Work')
        else :
            print('Not Work')
        tes_soil1 = 'T01 V0'
        self.ArdMntr.serial_send(tes_soil1)

    def btn_loadImg_click(self):
        dir_name, file_name = os.path.split(__file__)
        dir_name = os.path.join(dir_name, 'Data')
        str_imagePath = tkFileDialog.askopenfilename(title = "Select image",initialdir=dir_name, filetypes = (("jpeg files","*.jpg"), ("png files","*.png"), ("tif files","*.tif"),("all files","*.*")))
        print '>>>> ', str_imagePath
        if str_imagePath !="":
            img= utils_tool.readImage(str_imagePath)
            if img is not False:
                self.singleframe= img.copy()
                self.display_panel_singleframe(self.singleframe)
                Load_Image = pd.DataFrame([['38', 'Load Image' , 'True', 'True', 'Sucess']], index=['38'])
                Load_Image.to_excel(writer,'Sheet1', index=False, header=False, startrow=38, startcol= 0)
                writer.save()
            else:
                tkMessageBox.showerror('Image does not exist', 'The image\n{0}\n does not exist. Please check the path again')
                Load_Image = pd.DataFrame([['38', 'Load Image' , 'True', 'False', 'Failed']], index=['38'])
                Load_Image.to_excel(writer,'Sheet1', index=False, header=False, startrow=38, startcol= 0)
                writer.save()


    def btn_MoveTo_click(self):
        if self.ArdMntr.connect:
            try:
                Target_X= int(self.entry_Xpos.get())
                Target_Y= int(self.entry_Ypos.get())
                Target_Z= int(self.entry_Zpos.get())
                if (Target_X>=0) & (Target_X<=self.limit[0]) & (Target_Y>=0) & (Target_Y<=self.limit[1]):
                    cmd= 'G00 X{0} Y{1} Z{2}'.format(Target_X, Target_Y, Target_Z)
                    #self.ArdMntr.serial_send(cmd)
                    print 'ArdMntr.move_Coord...'
                    self.ArdMntr.move_Coord(Target_X, Target_Y, Target_Z)
                    print 'Command: ',cmd
                    time.sleep(1)

                else:
                    tkMessageBox.showerror("Error", "The range of X should be in [0~{0}]\nThe range of Y should be in [0~{1}]".format(self.limit[0],self.limit[1]))

            except:
                tkMessageBox.showerror("Error", "Please enter number!")
        else:
            tkMessageBox.showerror("Error", "Arduino connection refused!")



    def grid_display(self, frame):
        w1 = frame.shape[0] * 2 / 5
        h1 = frame.shape[1] * 2 / 5
        w2 = frame.shape[0] / 5
        h2 = frame.shape[1] / 5
        w3 = frame.shape[0] / 2
        h3 = frame.shape[1] / 2

        # Line Width 1
        cv2.line(frame , (h1 - h1 , w1) , (h3 + h3 , w1) , (255 , 0 , 0) , 1)
        # Line Height 1
        cv2.line(frame , (h1 , w1 - w1) , (h1 , w3 + w3) , (255 , 0 , 0) , 1)

        # Line Width 2
        cv2.line(frame , (h2 - h2 , w2), (h3 + h3 , w2) , (255, 0, 0) , 1)
        # Line Height 2
        cv2.line(frame , (h2 , w2 - w2) , (h2 , w3 + w3) , (255 , 0 , 0) ,1)

        # Line Width 3
        cv2.line(frame, (h1-h1, w1+w2), (h3 + h3 , w1+w2) , (255 , 0 , 0) , 1)
        # Line Height 3
        cv2.line(frame, (h1+h2, w1-w1) , (h1+h2, w3+w3), (255,0,0),1)

        # Line Width 4
        cv2.line(frame, (h1-h1, w1+w1), (h3 + h3 , w1+w1) , (255 , 0 , 0) , 1)
        #Line Height 4
        cv2.line(frame, (h1+h2*2,w1-w1), (h1+h2*2, w3+w3), (255,0,0),1)


        return frame

    def grids(self, frame):
        w1 = frame.shape[0]
        h1 = frame.shape[1]

        # Line Width 1
        cv2.line(frame , (h1 - h1 , w1-w1) , (w1-w1 , w1) , (255 , 0 , 0) , 5)
        # Line Height 1
        cv2.line(frame , (h1-h1 , w1 - w1) , (h1 , w1-w1 ) , (255 , 0 , 0) , 5)
        # Line Width 1
        cv2.line(frame , (h1 , w1) , (w1-w1 , w1) , (255 , 0 , 0) , 5)
        # Line Height 1
        cv2.line(frame , (h1, w1 ) , (h1 , w1-w1 ) , (255 , 0 , 0) , 5)
        return frame


    def mark_cross_line(self , frame):
        w1 = frame.shape[0] / 2
        h1 = frame.shape[1] / 2

        w2 = frame.shape[0] / 4
        h2 = frame.shape[1] / 4

        # Line Width 1
        cv2.line(frame , (h1 - h1 , w1) , (h1 + h1 , w1) , (255 , 0 , 0) , 1)
        # Line Height 1
        cv2.line(frame , (h1 , w1 - w1) , (h1 , w1 + w1) , (255 , 0 , 0) , 1)
        # Line Width 2
        cv2.line(frame , (h2 - h2 , w2), (h1 + h1 , w2) , (255, 0, 0) , 1)
        # Line Height 2
        cv2.line(frame , (h2 , w2 - w2) , (h2 , w1 + w1) , (255 , 0 , 0) ,1)

        # Line Width 3
        cv2.line(frame , (h2 - h2 , w1 + w2) , (h1 + h1 , w1 + w2) , (255, 0, 0), 1)
        # Line Height 3
        cv2.line(frame , (h2 + h1, w2 - w2), (h2 + h1, w1 + w1) , (255,0,0), 1)


        return frame

    def saveImg_function(self, arg_frame,arg_savePath, arg_filename):
        utils_tool.check_path(arg_savePath)
        # make sure output dir exists
        #if(not path.isdir(arg_savePath)):
        #    makedirs(arg_savePath)
        #tmp= cv2.cvtColor(arg_frame, cv2.COLOR_RGB2BGR)
        imageName = str(time.strftime("%Y_%m_%d_%H_%M_%S"))
        cv2.imwrite(arg_savePath +  imageName + '.jpg', arg_frame)
        #Bcv2.imwrite(arg_savePath + arg_filename + imageName + '.jpg', arg_frame)
        dir_name, file_name = os.path.split(__file__)
        dir_name = os.path.join(dir_name, 'Data')
        if imageName !="":
            Save_Image = pd.DataFrame([['37', 'Save & Display Capture Image' , 'True', 'True', 'Sucess']], index=['37'])
            Save_Image.to_excel(writer,'Sheet1', index=False, header=False, startrow=37, startcol= 0)
            writer.save()
        else :
            Save_Image = pd.DataFrame([['37', 'Display Camera to GUI', 'True', 'False', 'Failed']], index=['37'])
            Save_Image.to_excel(writer,'Sheet1', index=False, header=False, startrow=37, startcol= 0)
            writer.save()

    def runningScript_run(self):
        cmd_file = open('tmp.txt', "r")
        lines = cmd_file.readlines()
        for line in lines:
            cols = line.split("#")
            print '***', self.StartRunScript_judge,line
            print("line=%s,cols_count=%i" %(line,len(cols)))
            if len(cols)>=1:
                cmd = cols[0]
                cmd = cmd.strip()
                if len(cmd)>0:
                    print(">> "+cmd)
                    cmd_code= cmd.strip().split(' ')[0].replace(' ','')
                    if cmd_code[0]== 'C':
                        if cmd_code[1:]== '00':
                            TimeIndex= datetime.now().strftime('%Y%m%d%H%M%S')
                            tmp_x, tmp_y, tmp_z= self.ArdMntr.get_CurPosition()
                            imgName= '{0}_{1}_{2}_{3}'.format(TimeIndex, tmp_x, tmp_y, tmp_z)
                            self.singleframe= self.CamMntr.get_frame()
                            self.saveImg_function(self.singleframe, gui_vars.savePath, imgName)
                            self.display_panel_singleframe(self.singleframe)

                    else:
                        while 1:
                            if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
                                self.ArdMntr.serial_send("%s" %cmd)
                                time.sleep(1)
                                break
                            else:
                                time.sleep(1)
            time.sleep(1)
            if self.StartRunScript_judge== False:
                break
        #B cmd_file.close()
        #B print 'CLOSE FILE...'
        self.tabbox.tab(self.tab_control, state='normal')
        self.Lock_tabloadscript(False)
        self.btn_runscript.config(text= 'RUN', fg='white', activeforeground= 'white', bg= self.bgGreen,activebackground= self.bgGreen_active)
        self.StartRunScript_judge= False

    # Function Scanning
    def scanning_run(self):

        #while self.scanning_judge:
        if self.StartScan_judge:
            print '>>> Scanning...'

            if self.StartScan_judge == False:
                self.btn_StartScan.config(text= 'Start Scan', fg='white', activeforeground='white', bg=self.bgGreen, activebackground=self.bgGreen_active)
                self.root.update()
            else:
                self.btn_StartScan.config(text='Stop Scan', fg='white', activeforeground='white', bg=self.bgRed, activebackground=self.bgRed_active)
                self.root.update()
            step=0
            for step_X in range(0, self.scan_X[2]):
                if step_X < 1 :
                    self.after_1 = 0
                else :
                    self.after_1 = 1
                for step_Y in range(0, self.scan_Y[2]):
                    if self.StartScan_judge== False:
                        break

                    if step_X % 2 == 0:
                        tmp_step_Y = step_Y

                    else:
                        tmp_step_Y = self.scan_Y[2]- step_Y - 1

                    tmp_X, tmp_Y= self.scan_X[0]+ step_X*self.scan_X[1] *2  , self.scan_Y[0]+ tmp_step_Y * self.scan_Y[1] *2
                    #tmp_X, tmp_Y= self.scan_X[0] + step_X * self.scan_X[1], self.scan_Y[0] + step_Y * self.scan_Y[1]

                    print '>> X, Y: ', tmp_X, ', ', tmp_Y

                    #self.saveScanning= 'Raw_{0}_{1}.png'.format(self.scan_X[0]+ step_X * self.scan_X[1], self.scan_Y[0]+ step_Y * self.scan_Y[1])
                    self.ArdMntr.move_Coord(tmp_X, tmp_Y, self.input_Zpos)
                    time.sleep(1)
                    while 1:
                        if (self.ArdMntr.cmd_state.is_ready()):
                            time.sleep(0.5)
                            #self.saveScanning= '{0}_'.format(step)+self.ArdMntr.cmd_state.strCurX+'_'+self.ArdMntr.cmd_state.strCurY
                            #self.saveScanning= self.ArdMntr.cmd_state.strCurX+'_'+self.ArdMntr.cmd_state.strCurY
                            self.saveScanning= '{0}_{1}'.format(tmp_X, tmp_Y)
                            frame= self.CamMntr.get_frame()
                            self.saveImg_function(frame, gui_vars.saveScanningPath,self.readmergeframeIndex+'_'+self.saveTimeIndex+'_'+self.saveScanning)

                            result= frame.copy()
                            self.display_panel_singleframe(result)
                            #self.display_panel_mergeframe(result, step_X, step_Y)
                            #self.display_panel_mergeframe(result, step_Y, step_X)

                            #self.display_panel_mergeframe(result, tmp_step_Y, step_X)
                            self.display_panel_mergeframe(result, tmp_step_Y, self.scan_X[2] - 1 - step_X)   #2018.02.12
                            #print '>> display_panel X, Y: ', tmp_step_Y, ', ', self.scan_X[2] - 1 - step_X   #2018.02.12

                            print self.saveScanning
                            #time.sleep(2)
                            break
                        else:
                            time.sleep(1)
                    if self.StartScan_judge== False:
                        break
                    step= step+1
            self.StartScan_judge= False
            self.Lock_tabcontrol(False)
            self.Lock_Menubar(False)
            self.tabbox.tab(self.tab_loadscript, state='normal')
            self.btn_StartScan.config(text= 'Start Scan', fg='white', activeforeground='white', bg= self.bgGreen, activebackground= self.bgGreen_active)
        else:
            time.sleep(0.2)
            step=0

    def check_frame_update(self):
        result = Image.fromarray(self.frame)
        result = ImageTk.PhotoImage(result)
        self.panel.configure(image = result)
        self.panel.image = result
        self.panel.after(8, self.check_frame_update)

    def main_run(self):
        frame= self.CamMntr.get_frame()

        if frame is not -1:
            frame= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.grids(frame)
            frame= cv2.resize(frame,(self.frame_width,self.frame_height),interpolation=cv2.INTER_LINEAR)
            text='Arduino Connection Refused ...'
            text_water=''
            text_seed=''
            text_light=''	#2018.02.12
            color= (0, 0, 0)
            if self.ArdMntr.connect== True:
                if self.StartScan_judge == False:
                    if self.ArdMntr.cmd_state.is_ready() :
                        text= 'Idling ...'
                        color = (0 , 255 , 0)
                    else:
                        text= 'Moving ...'
                        color = (255,0,0)
                else:
                    if self.ArdMntr.cmd_state.is_ready():
                        text= 'Processing...'
                        color = (0 , 255 , 0)
                    else:
                        text= 'Scanning...'+'(X, Y)= ('+self.ArdMntr.cmd_state.strCurX+', '+self.ArdMntr.cmd_state.strCurY+')'
                        color = (255,0,0)
                if self.ArdMntr.WaterOn:
                    text_water= 'Water: On  '
                    cv2.putText(frame, text_water,(10,70),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0),1)
                if self.ArdMntr.SeedOn:
                    text_seed= 'Vaccum: On  '
                    cv2.putText(frame, text_seed,(10,100),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0),1)
                if self.ArdMntr.LightOn:
                    text_light= 'Light: On  '
                    cv2.putText(frame, text_light,(10,130),cv2.FONT_HERSHEY_SIMPLEX, 0.7,(255,0,0),1)
            cv2.putText(frame, text,(10,40),cv2.FONT_HERSHEY_SIMPLEX, 0.7,color,1)
            self.strStatus= text+ ' ; '+ text_water+ text_seed

            self.set_frame(frame)
        time.sleep(0.01)



    def watering_run(self):
        #while self.scanning_judge:
        if self.Start_Watering_judge:
            print '>>> Scanning...'

            step=0
            for step_X in range(0, self.scan_X[2]):
                if step_X < 1 :
                    self.after_1 = 0
                else :
                    self.after_1 = 1
                for step_Y in range(0, self.scan_Y[2]):
                    if self.StartScan_judge== False:
                        break

                    if step_X % 2 == 0:
                        tmp_step_Y = step_Y

                    else:
                        tmp_step_Y = self.scan_Y[2]- step_Y - 1

                    tmp_X, tmp_Y= self.scan_X[0]+ step_X*self.scan_X[1] *2  , self.scan_Y[0]+ tmp_step_Y * self.scan_Y[1] *2
                    #tmp_X, tmp_Y= self.scan_X[0] + step_X * self.scan_X[1], self.scan_Y[0] + step_Y * self.scan_Y[1]

                    print '>> X, Y: ', tmp_X, ', ', tmp_Y

                    #self.saveScanning= 'Raw_{0}_{1}.png'.format(self.scan_X[0]+ step_X * self.scan_X[1], self.scan_Y[0]+ step_Y * self.scan_Y[1])
                    self.ArdMntr.move_Coord(tmp_X, tmp_Y, self.input_Zpos)
                    time.sleep(1)
                    '''while 1:
                        self.ArdMntr.Water_Schedule(self.pinNumb_water, not(self.ArdMntr.WaterOn) , 5)
                        time.sleep(1)'''
                    check_soil = 'T01 V1'
                    self.ArdMntr.serial_send(check_soil)
                    check_soil = self.ArdMntr.cmd_state.strSoil
                    time.sleep(5)
                    if check_soil > 0 and check_soil < 2 :
                        cmd = 'F02 N{0}'.format(self.get_amount_water)
                        print(self.get_amount_water, 'ml')
                        self.serial_send(cmd)
                        water = int(self.get_amount_water)
                        db = sqlite3.connect('Database_Plant.db')
                        db.execute("UPDATE Plant_Database SET Amount_Water = (Amount_Water + ?) WHERE Location_Plant_X = ? AND Location_Plant_Y = ?" , (water, tmp_x, tmp_y,))
                        db.commit()
                        time.sleep(1)


                    if self.StartScan_judge== False:
                        break
                    step= step+1
            self.StartScan_judge= False
            self.Lock_tabcontrol(False)
            self.Lock_Menubar(False)
            self.tabbox.tab(self.tab_loadscript, state='normal')

        else:
            time.sleep(0.2)
            step=0

    def Plant_Detection_Go(self):
        from GUI import PlantDetectionGUI
        from PlantDetection import PlantDetection

        dir_name, file_name = os.path.split(__file__)
        dir_name = os.path.join(dir_name, 'Data')

        str_imagePath = tkFileDialog.askopenfilename(title = "Select image",initialdir=dir_name, filetypes = (("jpeg files","*.jpg"), ("png files","*.png"), ("tif files","*.tif"),("all files","*.*")))

        GUI = PlantDetectionGUI(image_filename= str_imagePath, plant_detection= PlantDetection)
        GUI.run()



    @staticmethod
    def hsv_trackbar_name(parameter, bound):
        """Create GUI trackbar name."""
        if parameter == 'H':
            parameter = 'Hue'
        if parameter == 'S':
            parameter = 'Saturation'
        if parameter == 'V':
            parameter = 'Value'
        return '{} {} {}'.format(parameter, bound, ' ' * (12 - len(parameter)))

    def _get_hsv_values(self):
        # get HSV values from sliders in HSV window
        for bound_num, bound in enumerate(['min', 'max']):
            for parameter in range(0, 3):
                self.hsv_bounds[bound_num][parameter] = cv2.getTrackbarPos(
                    self.hsv_trackbar_name('HSV'[parameter], bound),
                    self.hsv_window)


    def change_dropdown11(*args):
        print( tkvar11.get() )

    def change_dropdown12(*args):
        print( tkvar12.get())

    def change_dropdown21(*args):
        print(tkvar21.get())

    def change_dropdown22(*args):
        print(tkvar22.get())

    def change_dropdown31(*args):
        print(tkvar31.get())

    def change_dropdown32(*args):
        print(tkvar32.get())

root = Tkinter.Tk()
hidden1 = False
hidden2 = False

tkvar11 = StringVar(root)
tkvar12 = StringVar(root)
tkvar13 = StringVar(root)
tkvar21 = StringVar(root)
tkvar22 = StringVar(root)
tkvar31 = StringVar(root)
tkvar32 = StringVar(root)

global NAME_PLANT
global LOCATION_PLANT_X
global LOCATION_PLANT_Y
global LOCATION_PLANT_Z
global START_PLANT
global AGE_PLANT
global NOTE_PLANT


NAME_PLANT = StringVar()
LOCATION_PLANT_X = StringVar()
LOCATION_PLANT_Y = StringVar()
LOCATION_PLANT_Z = StringVar()
START_PLANT = StringVar()
AGE_PLANT = StringVar()
NOTE_PLANT = StringVar()

root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)

root.title("FARMBOT")
root.attributes('-zoomed', True) # FullScreen
#root.attributes('-fullscreen', True) #-2018.02.20
app= App(root)
root.mainloop()
