import Tkinter
import tkMessageBox
#from Tkinter import *
import tkSimpleDialog

class ToolsSetting(tkSimpleDialog.Dialog):
    # ########################################
    def __init__(self, master, arg_Seed, arg_Water):
        print 'init'
        self.Seed_Tool_Setting= arg_Seed
        self.Water_Tool_Setting= arg_Water
    	tkSimpleDialog.Dialog.__init__(self, master, "Tool Setting")
    # ########################################


    def body(self, master):
        print 'body'
        Tkinter.Label(master, text="Seed (X):").grid(row=0)
        Tkinter.Label(master, text="Seed (Y) :").grid(row=1)
        Tkinter.Label(master, text="Seed (Z):").grid(row=2)
        Tkinter.Label(master, text="Water (X) :").grid(row=3)
        Tkinter.Label(master, text="Water (Y):").grid(row=4)
        Tkinter.Label(master, text="Water (Z) :").grid(row=5)

        self.entry_Seed_X = Tkinter.Entry(master)
        self.entry_Seed_Y = Tkinter.Entry(master)
        self.entry_Seed_Z = Tkinter.Entry(master)
        self.entry_Water_X = Tkinter.Entry(master)
        self.entry_Water_Y = Tkinter.Entry(master)
        self.entry_Water_Z = Tkinter.Entry(master)
        self.entry_Seed_X.insert(Tkinter.END,self.Seed_Tool_Setting[0])
        self.entry_Seed_Y.insert(Tkinter.END,self.Seed_Tool_Setting[1])
        self.entry_Seed_Z.insert(Tkinter.END,self.Seed_Tool_Setting[2])
        self.entry_Water_X.insert(Tkinter.END,self.Water_Tool_Setting[0])
        self.entry_Water_Y.insert(Tkinter.END,self.Water_Tool_Setting[1])
        self.entry_Water_Z.insert(Tkinter.END,self.Water_Tool_Setting[2])

        self.entry_Seed_X.grid(row=0, column=1)
        self.entry_Seed_Y.grid(row=1, column=1)
        self.entry_Seed_Z.grid(row=2, column=1)
        self.entry_Water_X.grid(row=3, column=1)
        self.entry_Water_Y.grid(row=4, column=1)
        self.entry_Water_Z.grid(row=5, column=1)

        return self.entry_Seed_X # initial focus
        return self.entry_Seed_Y
        return self.entry_Seed_Z
        return self.entry_Water_X
        return self.entry_Water_Y
        return self.entry_Water_Z


    def apply(self):
        try:
            Numb_Seed_X = int(self.entry_Seed_X.get())
            Numb_Seed_Y = int(self.entry_Seed_Y.get())
            Numb_Seed_Z = int(self.entry_Seed_Z.get())
            Numb_Water_X = int(self.entry_Water_X.get())
            Numb_Water_Y = int(self.entry_Water_Y.get())
            Numb_Water_Z = int(self.entry_Water_Z.get())

            self.result= Numb_Seed_X, Numb_Seed_Y, Numb_Seed_Z, Numb_Water_X, Numb_Water_Y, Numb_Water_Z
            print Numb_Seed_X, Numb_Seed_Y, Numb_Seed_Z, Numb_Water_X, Numb_Water_Y, Numb_Water_Z # or something
        except ValueError:
            tkMessageBox.showwarning("Bad input","Illegal values, please try again")
