def watering_run(self):

      step=0
      self.input_Zpos= int(self.entry_Zpos.get())
      self.scan_X= [int(self.entry_1stXpos.get()), int(self.entry_ScanInterval_X.get()), int(self.entry_ScanAmount_X.get())]
      self.scan_Y= [int(self.entry_1stYpos.get()), int(self.entry_ScanInterval_Y.get()), int(self.entry_ScanAmount_Y.get())]

      self.ZposPara= 50
      #Load Soil Sensor
      with open("LoadSoil.txt") as f:
          with open("tmp.txt", "w") as f1:
              for line in f:
                  f1.write(line)
      cmd_file = open('tmp.txt', "r")
      lines = cmd_file.readlines()
      x_step = 0
      y_step= 0
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
                  while 1:
                      if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
                          self.ArdMntr.serial_send("%s" %cmd)
                          time.sleep(1)
                          break
                      else:
                          time.sleep(1)
      while 1:
          if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
              self.ArdMntr.move_Coord(self.scan_X[0], self.scan_Y[0], self.input_Zpos)
              time.sleep(1)
              break
          else:
              time.sleep(1)

      #while self.scanning_judge:
      step=0
      #while self.scanning_judge:
      if self.StartScan_judge:
          print '>>> Watering Running...'

          for step_X in range(0, self.scan_X[2]):
              x_step= x_step+1
              for step_Y in range(0, self.scan_Y[2]):
                  y_step= y_step+1
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
                  while 1:
                      if (self.ArdMntr.cmd_state.is_ready()):
                          self.ArdMntr.move_Coord(tmp_X, tmp_Y, self.input_Zpos)
                          time.sleep(1)
                          break

                  # Check Condition Soil Sensor
                  while 1:
                      #Soil_Data = int(self.ArdMntr.cmd_state.strSoil)

                      if (self.ArdMntr.cmd_state.is_ready()):
                          Soil_Data = int(self.ArdMntr.cmd_state.strSoil)
                          time.sleep(5)
                          print('Check Soil Data', Soil_Data)
                          if Soil_Data < self.get_Moisture_Max:
                              time.sleep(1)
                              while 1:
                                  if (self.ArdMntr.cmd_state.is_ready()):
                                      self.ArdMntr.move_Coord(tmp_X, tmp_Y, 0)
                                      time.sleep(1)
                                      break

                              with open("UnLoadSoilnLoadWater.txt") as f:
                                  with open("tmp.txt", "w") as f1:
                                      for line in f:
                                          f1.write(line)
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
                                          while 1:
                                              if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
                                                  self.ArdMntr.serial_send("%s" %cmd)
                                                  time.sleep(1)
                                                  break
                                              else:
                                                  time.sleep(1)
                                          time.sleep(1)
                              #Watering
                              while 1:
                                  if (self.ArdMntr.cmd_state.is_ready()):
                                      self.ArdMntr.move_Coord(tmp_X, tmp_Y, 0)
                                      break
                              while 1:
                                  if (self.ArdMntr.cmd_state.is_ready()):
                                      self.ArdMntr.switch_Water(self.pinNumb_water, not(self.ArdMntr.WaterOn) , -1)
                                      time.sleep(3)
                                      self.ArdMntr.switch_Water(self.pinNumb_water, not(self.ArdMntr.WaterOn) , -1)
                                      break

                              with open("UnLoadWater.txt") as f:
                                  with open("tmp.txt", "w") as f1:
                                      for line in f:
                                          f1.write(line)
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
                                          while 1:
                                              if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
                                                  self.ArdMntr.serial_send("%s" %cmd)
                                                  time.sleep(1)
                                                  break
                                              else:
                                                  time.sleep(1)
                                  time.sleep(1)
                              #Check Work or Not
                              print('Step_X >>>>>>', x_step)
                              print('Step_Y >>>>>>', y_step)
                              print('Step Acuan X >>>>>>', self.scan_X[2])
                              print('Step Acuan Y >>>>>>', self.scan_Y[2])


                              if x_step == (self.scan_X[2]) and y_step == self.scan_Y[2]*2:
                                  time.sleep(1)
                                  break
                              else:
                                  with open("LoadSoil.txt") as f:
                                      with open("tmp.txt", "w") as f1:
                                          for line in f:
                                              f1.write(line)
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
                                              while 1:
                                                  if self.ArdMntr.cmd_state.is_ready(): #wait system ready to accept commands
                                                      self.ArdMntr.serial_send("%s" %cmd)
                                                      time.sleep(1)
                                                      break
                                                  else:
                                                      time.sleep(1)
                                      time.sleep(1)
                                  break


                          else :
                              time.sleep(1)
                              while 1:
                                  if (self.ArdMntr.cmd_state.is_ready()):
                                      self.ArdMntr.move_Coord(tmp_X, tmp_Y, 0)
                                      break

                              break
                      else:
                          time.sleep(1)

                  if self.StartScan_judge== False:
                      break
                  step= step+1
          self.StartScan_judge= False
          x_step=0
          y_step=0
      else:
          time.sleep(0.2)
          step=0
