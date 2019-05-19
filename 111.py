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
            self.scan_X= [int(self.entry_1stXpos.get()), int(self.entry_ScanInterval_X.get()), int(self.entry_ScanAmount_X.get())]
            self.scan_Y= [int(self.entry_1stYpos.get()), int(self.entry_ScanInterval_Y.get()), int(self.entry_ScanAmount_Y.get())]

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
