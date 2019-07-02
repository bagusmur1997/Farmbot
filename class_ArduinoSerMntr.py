# verification code to verify serial connection
# program send serial F83 command every second to get FarmBot Arduion software version and print serial output out
# Ctrl-C can terminate program, pySerial needed.
# sample output, ver_cmd_mode = False:
#R83 GENESIS V.01.04
#
import threading
from serial import *
import time
import sys
import tkMessageBox
#from Farmbot_test_excel import *
#import pandas as pd
#from pandas import ExcelWriter
#from pandas import ExcelFile
import numpy as np

CMDSTATE_R00 = 0 #idle
CMDSTATE_R01 = 1 #running
CMDSTATE_R02 = 2 #end success
CMDSTATE_R03 = 3 #end with error
CMDSTATE_R04 = 4 #running
CMDSTATE_R82 = 82 #display the X Y Z position

RUNMODE_CHECKIF = 1
RUNMODE_VERIFY_CMDS=2
RUNMODE_CMDSCRIPT=3

class CmdState:
    def __init__(self):
        self.cmd_curid = ""
        self.cmd_curpar = ""
        self.cmd_str = ""
        self.cmd_state = CMDSTATE_R00

        # Initial Location
        self.strCurX= "0"
        self.strCurY= "0"
        self.strCurZ= "0"

        #Initial value
        self.strSoil = "0"

    def is_ready(self):
        if self.cmd_state == CMDSTATE_R00 or self.cmd_state == CMDSTATE_R02 or self.cmd_state == CMDSTATE_R03:
            return True
        else:
            return False

    def return_state(self):
        if self.cmd_state == CMDSTATE_R00 or self.cmd_state == CMDSTATE_R02 or self.cmd_state == CMDSTATE_R03:
            return 0
        elif self.cmd_state == CMDSTATE_R82:
            return 1
        else:
            return -1

    def set_by_send(self, cmd_str):
        if self.is_ready():
            self.cmd_state = CMDSTATE_R00
            self.cmd_str =  cmd_str

    def set_by_recv(self, cmd_str):
        cmd_str1 = cmd_str.strip().split(" ")
        #print cmd_str1,', ', cmd_str
        if cmd_str1[0] == "R00":
            self.cmd_state = CMDSTATE_R00
        if cmd_str1[0] == "R01":
            self.cmd_state = CMDSTATE_R01
        if cmd_str1[0] == "R02":
            self.cmd_state = CMDSTATE_R02
        if cmd_str1[0] == "R03":
            self.cmd_state = CMDSTATE_R03
        if cmd_str1[0] == "R04":
            self.cmd_state = CMDSTATE_R04
        if cmd_str1[0] == "R82":
            #self.cmd_state = CMDSTATE_R82
            self.strCurX= cmd_str1[1].strip('X')
            self.strCurY= cmd_str1[2].strip('Y')
            self.strCurZ= cmd_str1[3].strip('Z')
            #print '===> ',cmd_str1[1],', ',cmd_str1[2],', ',cmd_str1[3]
        if cmd_str1[0] == "Soil":
            self.strSoil= cmd_str1[3].strip('=').strip(' ').strip('%')
        self.cmd_str = cmd_str.strip()
        #print("state by recv:%i" %(self.cmd_state))

# Serial process thread
# >> defualt time interval: 0.01 sec
class MonitorThread(threading.Thread):
    def __init__(self, wait=0.01):
        threading.Thread.__init__(self)
        self.event = threading.Event()
        self.wait = wait
        self.exit = False
        self.connect = False
        self.WaterOn= False
        self.SeedOn= False
        self.LightOn= False
        self.E_StopOn= False
        self.FanOn= False
        self.MoistureOn= False
        self.channel=['/dev/ttyACM0', '/dev/ttyACM1', '/dev/ttyACM2', '/dev/ttyUSB0', '/dev/tty0']
        self.connect_serial()
        self.cmd_state = CmdState()

    def connect_serial(self):
        if not(self.connect):
            try:
                for tmp_channel in self.channel:
                    try:
                        self.ser = Serial(tmp_channel, 115200, timeout=1) #FIXME, cha    nge device id to your system device
                        print tmp_channel,': connected successfully!'
                        self.connect= True
                        #Connect_Arduino = pd.DataFrame([['1', 'Connect to Arduino', 'Number Channel Arduino":Connected Successfully"', tmp_channel + ': Connection Successfully', 'Success' ]], columns=['No', 'Action', 'Output Needed', 'Result', 'Status'])
                        #Connect_Arduino.to_excel(writer,'Sheet1', index=False, header=True, startrow=0, startcol= 0)
                        #writer.save()
                        break
                    except:
                        print tmp_channel,': connection Refused!'
                        #Connect_Arduino = pd.DataFrame([['1', 'Connect to Arduino', 'Number Channel Arduino":Connected Successfully"', tmp_channel + ': Connection Refused', 'Fail' ]], columns=['No', 'Action', 'Output Needed', 'Result', 'Status'])
                        #Connect_Arduino.to_excel(writer,'Sheet1', index=False, header=True, startrow=0, startcol= 0)
                        #writer.save()

            except:
                print 'Connection of Arduino refused!'
                tkMessageBox.showerror("Error","Connection of Arduino refused!")
                print tmp_channel,': connection Refused!'
                #Connect_Arduino = pd.DataFrame([['1', 'Connect to Arduino', 'Number Channel Arduino ":Connected Successfully"', 'Error Connection Arduino Refused', 'Fail' ]], columns=['No', 'Action', 'Output Needed', 'Result', 'Status'])
                #Connect_Arduino.to_excel(writer,'Sheet1', index=False, header=True, startrow=0, startcol= 0)
                #writer.save()
        else:
            tkMessageBox.showerror("Error", "Connection of Arduino is already built!")





    def set_ts(self, ts):
        self.wait = ts

    def do_function(self):
        #print("thread running...")
        #line = self.ser.read(self.ser.inWaiting()) # read everything in the input buffer
        line = self.ser.readline()
        if len(line)>0:
            #print(line)
            sys.stdout.write(line)
            self.cmd_state.set_by_recv(line)

    def run(self):
        while 1:
            if self.connect:
                try:
                    self.do_function()
                    self.event.wait(self.wait)
                except:
                    self.connect= False
            else:
                time.sleep(0.1)

            if self.exit:
                break

    def serial_send(self,send_str):
        sys.stdout.write("[%s]\n" % send_str)
        self.ser.write(send_str + " \r\n")
        self.cmd_state.set_by_send(send_str)

    def Water_Schedule(self, arg_pinNumb=9, arg_On=False, arg_delay=3):
        if arg_On:
            #self.serial_send('F41 P9 V1 M0')
            self.serial_send('F41 P{0} V1 M0'.format(arg_pinNumb))	#2018.02.28
            self.WaterOn= True
            print 'Watering On... '
            txt= 'Scheduling Watering : Water Pump On'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()
            if arg_delay== 0:
                #self.serial_send('F41 P9 V0 M0')
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
                self.WaterOn= False
                print 'Watering Off... '
                txt= 'Scheduling Watering : Water Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
                db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
                db.commit()
                db.close()
            elif arg_delay> 0:
                time.sleep(arg_delay)
                #self.serial_send('F41 P9 V0 M0')
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
                self.WaterOn= False
                print 'Watering Off... '
                txt= 'Scheduling Watering : Water Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
                db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
                db.commit()
                db.close()
        else:
            #self.serial_send('F41 P9 V0 M0')
            self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
            self.WaterOn= False
            print 'Watering Off... '
            txt= 'Scheduling Watering : Water Pump Off'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()

    def Seed_Schedule(self, arg_pinNumb=10, arg_On=True, arg_delay=20):
        if arg_On:
            self.serial_send('F41 P{0} V1 M0'.format(arg_pinNumb))
            self.SeedOn= True
            print 'Seeding On... '
            txt= 'Planting : Vaccum Pump On'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()
            if arg_delay== 0:
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))
                self.SeedOn= False
                print 'Seeding Off... '
                txt= 'Planting : Vaccum Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
            	db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            	db.commit()
                db.close()
            elif arg_delay> 0:
                time.sleep(arg_delay)
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))
                self.SeedOn= False
                print 'Seeding Off... '
                txt= 'Planting : Vaccum Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
            	db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            	db.commit()
                db.close()
        else:
            self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))
            self.SeedOn= False
            print 'Seeding Off... '
            txt= 'Planting : Vaccum Pump Off'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()



    def switch_Water(self, arg_pinNumb=9, arg_On=False, arg_delay=-1):
        if arg_On:
            #self.serial_send('F41 P9 V1 M0')
            self.serial_send('F41 P{0} V1 M0'.format(arg_pinNumb))	#2018.02.28
            self.WaterOn= True
            txt= 'Water Pump On'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()

            if arg_delay== 0:
                #self.serial_send('F41 P9 V0 M0')
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
                self.WaterOn= False
                txt= 'Water Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
                db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
                db.commit()
                db.close()
            elif arg_delay> 0:
                time.sleep(arg_delay)
                #self.serial_send('F41 P9 V0 M0')
                self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
                self.WaterOn= False
                txt= 'Water Pump Off'
                print(txt)
                db = sqlite3.connect('Database_Log.db')
                db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
                db.commit()
                db.close()
        else:
            #self.serial_send('F41 P9 V0 M0')
            self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
            self.WaterOn= False
            txt= 'Water Pump Off'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()

    def switch_Seed(self, arg_pinNumb=10, arg_On=True):
        if arg_On:
            self.serial_send('F41 P{0} V1 M0'.format(arg_pinNumb))
            self.SeedOn= True
            txt= 'Vaccum Pump On'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()
        else:
            self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))
            self.SeedOn= False
            txt= 'Vaccum Pump Off'
            print(txt)
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'),?)", [txt])
            db.commit()
            db.close()


    def switch_Light(self, arg_pinNumb=8, arg_On=True):     #2018.02.12 arg_on -> arg_On
        if arg_On:
            self.serial_send('F41 P{0} V1 M0'.format(arg_pinNumb))	#2018.02.28
            #self.serial_send('F41 P8 V1 M0')  #2018.02.12 {0}->8
            self.LightOn= True

            txt= 'Light On'
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'), ?)",
                        [txt])
            db.commit()
        else:
            self.serial_send('F41 P{0} V0 M0'.format(arg_pinNumb))	#2018.02.28
            #self.serial_send('F41 P8 V0 M0')  #2018.02.12 {0}->8
            self.LightOn= False

            txt= 'Light Off'
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'), ?)",
                        [txt])
            db.commit()

    def E_Stop(self, arg_On=True):
        if arg_On:
            self.serial_send('E')
            self.E_StopOn= True

            txt= 'Push Emergency Stop'
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'), ?)",
                        [txt])
            db.commit()
        else:
            self.serial_send('F09')
            self.E_StopOn= False
            txt= 'Reset Emergency Stop'
            db = sqlite3.connect('Database_Log.db')
            db.execute("insert into Database_Log (Time, Action) values (datetime('now', 'localtime'), ?)",
                        [txt])
            db.commit()


    def switch_Moisture(self, arg_On=True):
        Moisture3 = 'T01 V1'
        Moisture4 = 'T01 V0'
        if arg_On:
            self.serial_send(Moisture3)
            self.MoistureOn= True
        else :
            self.serial_send(Moisture4)
            self.MoistureOn = False
            self.strSoil = "0"


    def move_Coord(self, arg_Xpos, arg_Ypos, arg_Zpos):
        cmd= 'G00 X{0} Y{1} Z{2}'.format(arg_Xpos, arg_Ypos, arg_Zpos)
        self.serial_send(cmd)
        time.sleep(0.5)

        while True:
            tmp_x , tmp_y , tmp_z = self.get_CurPosition()
            if tmp_x == arg_Xpos and tmp_y == arg_Ypos and tmp_z == arg_Zpos :
                #Move_Coor = pd.DataFrame([['33', 'Move to Coordinates' , 'X:' + str(arg_Xpos) + ', Y:' + str(arg_Ypos) + ', Z:' + str(arg_Zpos), 'X:' + str(tmp_x) + ', Y:' + str(tmp_y) + ', Z:' + str(tmp_z), 'Success']], index=['33'])
                #Move_Coor.to_excel(writer,'Sheet1', index=False, header=False, startrow=33, startcol= 0)
                #writer.save()
                break
            else:
                #Move_Coor = pd.DataFrame([['33', 'Move to Coordinates' , 'X:' + str(arg_Xpos) + ', Y:' + str(arg_Ypos) + ', Z:' + str(arg_Zpos), 'X:' + str(tmp_x) + ', Y:' + str(tmp_y) + ', Z:' + str(tmp_z), 'Failed']], index=['33'])
                #Move_Coor.to_excel(writer,'Sheet1', index=False, header=False, startrow=33, startcol= 0)
                #writer.save()
                break


    def get_CurPosition(self):
        #tmp_x= int(self.cmd_state.strCurX)
        #tmp_y= int(self.cmd_state.strCurY)
        #tmp_z= int(self.cmd_state.strCurZ)
        tmp_x= float(self.cmd_state.strCurX)	#2018.02.28-For v6.0.1
        tmp_y= float(self.cmd_state.strCurY)	#2018.02.28-For v6.0.1
        tmp_z= float(self.cmd_state.strCurZ)    #2018.02.28-For v6.0.1

        return tmp_x, tmp_y, tmp_z

    def get_SoilData(self):

        soildata = int(self.cmd_state.strSoil)

        return soildata

    def set_MaxSpeed(self, arg_spd, arg_index):
        if arg_index.lower() == 'x':
            cmd= 'F22 P71 V{0}'.format(arg_spd)

        elif arg_index.lower() == 'y' :
            cmd= 'F22 P72 V{0}'.format(arg_spd)
        else:
            cmd= 'F22 P73 V{0}'.format(arg_spd)
        self.serial_send(cmd)
        time.sleep(0.05)

    def set_Acceleration(self, arg_acc, arg_index):
        if arg_index.lower() == 'x':
            cmd= 'F22 P41 V{0}'.format(arg_acc)
        elif arg_index.lower() == 'y' :
            cmd= 'F22 P42 V{0}'.format(arg_acc)
        else:
            cmd= 'F22 P43 V{0}'.format(arg_acc)
        self.serial_send(cmd)
        time.sleep(0.05)

'''
def main():

    th = MonitorThread()
    th.start()

    cmd_delay_second =1
    wait_ready_second =3
    run_mode = RUNMODE_CHECKIF # RUNMODE_CHECKIF, RUNMODE_VERIFY_CMDS(default), RUNMODE_CMDSCRIPT,

    file_name = "serial_commands_list.txt"
    if run_mode == RUNMODE_CMDSCRIPT:
        file_name = "serial_script.txt"


    while 1:
        try:
            if run_mode == RUNMODE_CHECKIF:
                th.serial_send("F83")
                time.sleep(1)

            else : # verify current commands.
                cmd_file = open(file_name, "r")
                lines = cmd_file.readlines()
                for line in lines:

                    cols = line.split("#")
                    #print("line=%s,cols_count=%i" %(line,len(cols)))
                    if len(cols)>=1:
                        cmd = cols[0]
                        cmd = cmd.strip()
                        if len(cmd)>0:
                            #print(cmd)
                            while 1:
                                if th.cmd_state.is_ready(): #wait system ready to accept commands
                                    th.serial_send("%s" %cmd)
                                    time.sleep(wait_ready_second)
                                    break
                                else:
                                    time.sleep(wait_ready_second)
                            #ser.write("F83\n")
                    time.sleep(cmd_delay_second)
                cmd_file.close()

                th.exit = True
                break

        except:
            th.exit = True
            print 'Except happened'
            break

if __name__ == "__main__":
    main()
'''
