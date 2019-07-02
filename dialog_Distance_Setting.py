import Tkinter
import tkMessageBox
#from Tkinter import *
import tkSimpleDialog

class DistanceSetting(tkSimpleDialog.Dialog):
    # ########################################
    def __init__(self, master, arg_Distance_Watering, arg_Distance_Soil, arg_Distance_Seeding):
        print 'init'
        self.Distance_Soil_para= arg_Distance_Soil
        self.Distance_Watering_para= arg_Distance_Watering
        self.Distance_Seeding_para= arg_Distance_Seeding
    	tkSimpleDialog.Dialog.__init__(self, master, "Distance Setting")
    # ########################################


    def body(self, master):
        print 'body'
        Tkinter.Label(master, text="Distance Watering (Z)").grid(row=0)
        Tkinter.Label(master, text="Distance Soil Sensor (Z)").grid(row=1)
        Tkinter.Label(master, text="Distance Seeding (Z)").grid(row=2)

        self.entry_Distance_Watering = Tkinter.Entry(master)
        self.entry_Distance_Soil = Tkinter.Entry(master)
        self.entry_Distance_Seeding = Tkinter.Entry(master)

        self.entry_Distance_Watering.insert(Tkinter.END,str(self.Distance_Watering_para[0]))
        self.entry_Distance_Soil.insert(Tkinter.END,str(self.Distance_Soil_para[0]))
        self.entry_Distance_Seeding.insert(Tkinter.END,self.Distance_Seeding_para[0])

        self.entry_Distance_Watering.grid(row=0, column=1)
        self.entry_Distance_Soil.grid(row=1, column=1)
        self.entry_Distance_Seeding.grid(row=2, column=1)

        return self.entry_Distance_Watering # initial focus

    def apply(self):
        try:
            Distance_Watering = int(self.entry_Distance_Watering.get())
            Distance_Soil = int(self.entry_Distance_Soil.get())
            Distance_Seeding = int(self.entry_Distance_Seeding.get())

            self.result= Distance_Watering, Distance_Soil, Distance_Seeding
            print Distance_Watering, Distance_Soil, Distance_Seeding # or something
        except ValueError:
            tkMessageBox.showwarning("Bad input","Illegal values, please try again")
