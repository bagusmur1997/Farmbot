#while self.scanning_judge:
if self.StartScan_judge:
    print '>>> Watering...'
    step=0
    for step_X in range(0, self.scan_X[2]):
        for step_Y in range(0, self.scan_Y[2]):
            if self.StartScan_judge== False:
                break
            if step_X % 2 ==0:
                tmp_step_Y= step_Y
            else:
                tmp_step_Y= self.scan_Y[2]- step_Y-1
            tmp_X, tmp_Y= self.scan_X[0]+ step_X*self.scan_X[1], self.scan_Y[0]+ tmp_step_Y*self.scan_Y[1]
            #tmp_X, tmp_Y= self.scan_X[0]+ step_X*self.scan_X[1], self.scan_Y[0]+ step_Y*self.scan_Y[1]
            print '>> X, Y: ', tmp_X, ', ', tmp_Y
            #self.saveScanning= 'Raw_{0}_{1}.png'.format(self.scan_X[0]+ step_X*self.scan_X[1], self.scan_Y[0]+ step_Y*self.scan_Y[1])
            self.ArdMntr.move_Coord(tmp_X, tmp_Y, self.input_Zpos)
            time.sleep(1)
            while 1:
                if (self.ArdMntr.cmd_state.is_ready()):
                    time.sleep(0.5)
                    #self.ArdMntr.Water_Schedule(self.pinNumb_water, not(self.ArdMntr.WaterOn) , 5)
                    time.sleep(1)

            #tes_soil = 'T01 V1'
            #self.ArdMntr.serial_send(tes_soil)
            #time.sleep(10)
            #soil_data = float(self.ArdMntr.cmd_state.strSoil)
            #print('Test Soil :')
            #print(soil_data)
            #soil_min = self.get_Moisture_Min
            #soil_max = self.get_Moisture_Max
            #if soil_data > soil_min and soil_data < soil_max :
                #cmd = 'F02 N{0}'.format(self.get_amount_water)
                #print(self.get_amount_water, 'ml')
                #self.serial_send(cmd)
                #water = int(self.get_amount_water)
                #db = sqlite3.connect('Database_Plant.db')
                #db.execute("UPDATE Plant_Database SET Amount_Water = (Amount_Water + ?) WHERE Location_Plant_X = ? AND Location_Plant_Y = ?" , (water, tmp_x, tmp_y,))
                #db.commit()
                #time.sleep(1)
            else :
                print('Not Work')
            #tes_soil1 = 'T01 V0'
            #self.ArdMntr.serial_send(tes_soil1)

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
