import Tkinter
import tkMessageBox
import tkFont
#from Tkinter import *
import tkSimpleDialog

class ToolSetting(tkSimpleDialog.Dialog):
    # ########################################
    def __init__(self, master, arg_ToolList=[('',0, 0, 0)]):
        print 'init'
        strFont= 'Arial'
        self.__myfont12 = tkFont.Font(family=strFont, size=12)
        self.__myfont12_Bold = tkFont.Font(family=strFont, size=12, weight= tkFont.BOLD)
        self.__myfont10 = tkFont.Font(family=strFont, size=10)
        self.__myfont10_Bold = tkFont.Font(family=strFont, size=10, weight= tkFont.BOLD)
        self.__ToolList= arg_ToolList
        self.__MaxRow= 7
        self.__CurrentRow= len(arg_ToolList)
        self.__CurGridRow= self.__CurrentRow
        self.__NumberList= range(0, self.__MaxRow+1)
        self.__entries_Tools= [0]
        self.__entries_LocX= [0]
        self.__entries_LocY= [0]
        self.__entries_LocZ= [0]
        self.__btns_clear=[0]
        #self.master= master
    	tkSimpleDialog.Dialog.__init__(self, master, "Tools")
    # ########################################


    def body(self, master):
        print 'body of Dialog Tools'
        Tkinter.Label(master, text="Tools", font= self.__myfont12_Bold).grid(row=0, column=0)
        Tkinter.Label(master, text="X", font= self.__myfont12_Bold).grid(row=0, column=1)
        Tkinter.Label(master, text="Y", font=self.__myfont12_Bold).grid(row=0, column=2)
        Tkinter.Label(master, text="Z", font=self.__myfont12_Bold).grid(row=0, column=3)
        Tkinter.Button(master, text= '+', font= self.__myfont12_Bold, command= self.btn_add_click, fg='white',activeforeground= 'white', bg= '#007700', activebackground= '#00aa00').grid(row=0,column=4)

        for i in self.__NumberList:
            if i==0:
                continue
            en_tool = Tkinter.Entry(master)
            self.__entries_Tools.append(en_tool)

            en_locx= Tkinter.Entry(master)
            self.__entries_LocX.append(en_locx)

            en_locy= Tkinter.Entry(master)
            self.__entries_LocY.append(en_locy)

            en_locz= Tkinter.Entry(master)
            self.__entries_LocZ.append(en_locz)

            btn= Tkinter.Button(master, text= '-', font= self.__myfont12_Bold, command= lambda i=i: self.btn_clear_click(i),fg='white',activeforeground= 'white', bg= '#aa0000', activebackground= '#ee0000')
            self.__btns_clear.append(btn)

            if i <=  self.__CurrentRow:
                en_tool.insert(Tkinter.END, self.__ToolList[i-1][0])
                #en_func.insert(Tkinter.END, '{0}'.format(i))
                en_locx.insert(Tkinter.END, self.__ToolList[i-1][1])
                en_locy.insert(Tkinter.END, self.__ToolList[i-1][2])
                en_locz.insert(Tkinter.END, self.__ToolList[i-1][3])
                #'''
                en_tool.grid(row=i,column=0)
                en_locx.grid(row=i, column=1)
                en_locy.grid(row=i, column=2)
                en_locz.grid(row=i, column=3)
                btn.grid(row=i,column=4)
                '''
                en_func.grid_remove()
                en_pinnumb.grid_remove()
                btn.grid_remove()
                #'''
            #self.add_Row( i)
        return self.__entries_Tools[0] # initial focus

    def apply(self):
        try:
            self.result=[]
            for i in range(1, len(self.__entries_Tools)):
                r1, r2, r3, r4= self.__entries_Tools[i].get(), self.__entries_LocX[i].get(), self.__entries_LocY[i].get(), self.__entries_LocZ[i].get()
                if r1 != '' and r2 != '' and r3 != '' and r4 != '':
                    self.result.append([r1, r2, r3, r4])
            #print 'result:', self.result
            print 'End of dialog' # or something
        except ValueError:
            tkMessageBox.showwarning("Bad input","Illegal values, please try again")

    def btn_clear_click(self, arg_index):
        clear_row= self.__NumberList.index(arg_index)
        '''
        print '============= CLEAR ============'
        print 'Clear Row:', clear_row
        print 'NumberLIst:', self.__NumberList
        print 'clear_index', arg_index
        gridInfo= self.__entries_Func[arg_index].grid_info()
        #print gridInfo
        print 'Clear Grid Row', gridInfo['row']
        #'''
        #'''
        self.__entries_Tools[arg_index].delete(0, 'end')
        self.__entries_LocX[arg_index].delete(0, 'end')
        self.__entries_LocY[arg_index].delete(0, 'end')
        self.__entries_LocZ[arg_index].delete(0, 'end')

        self.__entries_Tools[arg_index].grid_forget()
        self.__entries_LocX[arg_index].grid_forget()
        self.__entries_LocY[arg_index].grid_forget()
        self.__entries_LocZ[arg_index].grid_forget()
        self.__btns_clear[arg_index].grid_forget()


        '''
        self.__entries_Func[arg_index].grid_remove()
        self.__entries_PinNumb[arg_index].grid_remove()
        self.__btns_clear[arg_index].grid_remove()
        #'''
        tmp= self.__NumberList[clear_row]
        del self.__NumberList[clear_row]
        self.__NumberList.append(tmp)
        self.__CurrentRow= self.__CurrentRow-1
        #print '__CurrentRow:', self.__CurrentRow
        #'''
    def btn_add_click(self):
        '''
        print '============= ADD ============'
        print '### Current Row', self.__CurrentRow
        print 'NumberLIst:', self.__NumberList
        for i in range(1,len(self.__entries_Func)):
            tmp= self.__NumberList[i]
            gridInfo= self.__entries_Func[tmp].grid_info()
            if len(gridInfo)!=0:
                print 'Row ',str(i),' Entries List[', str(tmp),']: ', self.__entries_Func[tmp].grid_info()['row']
            else:
                print 'Row ',str(i),' empty'
        #'''
        if self.__CurrentRow < self.__MaxRow:
            self.__CurrentRow= self.__CurrentRow+1
            self.__CurGridRow= self.__CurGridRow+1
            #self.__CurGridRow= self.__CurrentRow
            add_index= self.__NumberList[self.__CurrentRow]
            '''
            print 'Added Row:', self.__CurrentRow
            print 'add_index (NumberList[{0}]): {1}'.format(self.__CurrentRow,add_index)
            print 'Grid Row:', self.__CurGridRow
            #'''
            self.__entries_Tools[add_index].grid(row=self.__CurGridRow, column=0)
            #self.__entries_Func[add_index].delete(0, 'end')
            self.__entries_LocX[add_index].grid(row=self.__CurGridRow, column=1)
            #self.__entries_PinNumb[add_index].delete(0, 'end')
            self.__entries_LocY[add_index].grid(row=self.__CurGridRow, column=2)
            self.__entries_LocZ[add_index].grid(row=self.__CurGridRow, column=3)
            self.__btns_clear[add_index].grid(row=self.__CurGridRow, column=4)
            #print 'Row ',str(self.__CurrentRow),' Entries List[', str(add_index),']: ', self.__entries_Func[add_index].grid_info()['row']
        elif self.__CurrentRow== self.__MaxRow:
            print 'Max of Row is ', self.__MaxRow
