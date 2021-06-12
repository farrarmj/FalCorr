#GUI for setting of experimental parameters in DLS GUI

import sys
try:
    from Tkinter import *
except ImportError:
    from tkinter import *

try:
    import ttk
    py3 = False
except ImportError:
    import tkinter.ttk as ttk
    py3 = True


def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root
    root = Tk()
    top = OptionWindow(root)
    root.mainloop()

def create_New_OptionWindow(root, mode = 'normal'):
    '''Starting point when module is imported by another program.'''
    global w, w_win, rt
    rt = root
    w = Toplevel (root)
    top = OptionWindow (w,mode)
    Tk.wait_window(w) #This is critical to letting the updated GUI parameters be returned
    return (w, top)

def destroy_OptionWindow():
    global w
    w.destroy()
    w = None


class OptionWindow:
    def __init__(self, top=None,mode = 'normal'):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85' 
        _ana2color = '#d9d9d9' # X11 color: 'gray85' 
        font10 = "-family {Segoe UI} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"
        font9 = "-family {Courier New} -size 12 -weight normal -slant "  \
            "roman -underline 0 -overstrike 0"

        top.geometry("350x300+154+102")
        top.title("Experiment Parameters")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")

        #Key Quantities We Want to Determine
        self.newData = "Yes"
        self.acqDur = 300
        self.maxNumTrials=1
        self.correlations = [1,1,1,1] #correlation pairs to compute and/or bin counts

        #Popup menu and label for Acquisition Duration
        self.Label1 = Label(top)
        self.Label1.place(relx=0.01, rely=0.02, height=51, width=154)
        self.Label1.configure(activebackground="#f9f9f9")
        self.Label1.configure(activeforeground="black")
        self.Label1.configure(background="#d9d9d9")
        self.Label1.configure(disabledforeground="#a3a3a3")
        self.Label1.configure(font=font10)
        self.Label1.configure(foreground="#000000")
        self.Label1.configure(highlightbackground="#d9d9d9")
        self.Label1.configure(highlightcolor="black")
        self.Label1.configure(text='''Acquisition Time (s)''')

        self.timeVar = StringVar(top)
        self.timeVar.set(str(self.acqDur)) # default value
        self.acqTimes = OptionMenu(top, self.timeVar,"10","30","100","300","1000")
        self.acqTimes.configure(activebackground="#f9f9f9")
        self.acqTimes.configure(activeforeground="black")
        self.acqTimes.configure(background="#d9d9d9")
        self.acqTimes.configure(state = mode)
        self.acqTimes.configure(font=font10,justify=CENTER)
        self.acqTimes.pack()
        self.acqTimes.place(relx=0.10, rely=0.17,height=41, width=80)
        

        #entry and label for Number oF Trials
        self.Label2 = Label(top)
        self.Label2.place(relx=0.47, rely=0.02, height=51, width=184)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(activeforeground="black")
        self.Label2.configure(background="#d9d9d9")
        self.Label2.configure(disabledforeground="#a3a3a3")
        self.Label2.configure(font=font10)
        self.Label2.configure(foreground="#000000")
        self.Label2.configure(highlightbackground="#d9d9d9")
        self.Label2.configure(highlightcolor="black")
        self.Label2.configure(text='''Num. Trials''')

        #Entry 
        self.maxTrialStr = StringVar(top)
        self.maxTrials = Entry(top)
        self.maxTrials.place(relx=0.60, rely=0.20,height=30, relwidth=0.25)
        self.maxTrials.configure(background="white")
        self.maxTrials.configure(validate = "focus")
        self.maxTrials.configure(disabledforeground="#a3a3a3")
        self.maxTrials.configure(font=font10, justify = CENTER)
        self.maxTrials.configure(foreground="#000000")
        self.maxTrials.configure(highlightbackground="#d9d9d9")
        self.maxTrials.configure(highlightcolor="black")
        self.maxTrials.configure(insertbackground="black")
        self.maxTrials.configure(selectbackground="#c4c4c4")
        self.maxTrials.configure(selectforeground="black")
        self.maxTrials.configure(textvariable=self.maxTrialStr)
        self.maxTrials.bind("<FocusOut>",self.validateNumTrials)
        self.maxTrialStr.set(str(1))

        #Label for correlations
        self.Label3 = Label(top)
        self.Label3.place(relx=0.22, rely=0.35, height=51, width=184)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(activeforeground="black")
        self.Label3.configure(background="#d9d9d9")
        self.Label3.configure(disabledforeground="#a3a3a3")
        self.Label3.configure(font=font10)
        self.Label3.configure(foreground="#000000")
        self.Label3.configure(highlightbackground="#d9d9d9")
        self.Label3.configure(highlightcolor="black")
        self.Label3.configure(text='''Correlations to Compute''')
        

        #Correlations To Compute
        self.Ch1ACFVar = IntVar()
        self.Ch1ACFVar.set(1)
        self.Ch1xCh1 = Checkbutton(top,text = 'Ch1 ACF')
        self.Ch1xCh1.configure(activebackground="#f9f9f9")
        self.Ch1xCh1.configure(activeforeground="black")
        self.Ch1xCh1.configure(background="#f9f9f9")
        self.Ch1xCh1.configure(disabledforeground="#a3a3a3")
        self.Ch1xCh1.configure(font=font10)
        self.Ch1xCh1.configure(foreground="#000000")
        self.Ch1xCh1.configure(highlightbackground="#d9d9d9")
        self.Ch1xCh1.configure(highlightcolor="black")
        self.Ch1xCh1.configure(variable = self.Ch1ACFVar)
        self.Ch1xCh1.pack()
        self.Ch1xCh1.place(relx=0.15, rely=0.50,height=30, relwidth=0.30)
        
        self.Ch1xCh2Var = IntVar()
        self.Ch1xCh2Var.set(1)
        self.Ch1xCh2 = Checkbutton(top,text = 'Ch1 x Ch2')
        self.Ch1xCh2.configure(activebackground="#f9f9f9")
        self.Ch1xCh2.configure(activeforeground="black")
        self.Ch1xCh2.configure(background="#f9f9f9")
        self.Ch1xCh2.configure(disabledforeground="#a3a3a3")
        self.Ch1xCh2.configure(font=font10)
        self.Ch1xCh2.configure(foreground="#000000")
        self.Ch1xCh2.configure(highlightbackground="#d9d9d9")
        self.Ch1xCh2.configure(highlightcolor="black")
        self.Ch1xCh2.configure(variable = self.Ch1xCh2Var)
        self.Ch1xCh2.pack()
        self.Ch1xCh2.place(relx=0.55, rely=0.50,height=30, relwidth=0.30)
        
        self.Ch2xCh1Var = IntVar()
        self.Ch2xCh1Var.set(1)
        self.Ch2xCh1 = Checkbutton(top,text = 'Ch2 x Ch1')
        self.Ch2xCh1.configure(activebackground="#f9f9f9")
        self.Ch2xCh1.configure(activeforeground="black")
        self.Ch2xCh1.configure(background="#f9f9f9")
        self.Ch2xCh1.configure(disabledforeground="#a3a3a3")
        self.Ch2xCh1.configure(font=font10)
        self.Ch2xCh1.configure(foreground="#000000")
        self.Ch2xCh1.configure(highlightbackground="#d9d9d9")
        self.Ch2xCh1.configure(highlightcolor="black")
        self.Ch2xCh1.configure(variable = self.Ch2xCh1Var)
        self.Ch2xCh1.pack()
        self.Ch2xCh1.place(relx=0.15, rely=0.60,height=30, relwidth=0.3)
        
        self.Ch2ACFVar = IntVar()
        self.Ch2ACFVar.set(1)
        self.Ch2xCh2 = Checkbutton(top,text = 'Ch2 ACF')
        self.Ch2xCh2.configure(activebackground="#f9f9f9")
        self.Ch2xCh2.configure(activeforeground="black")
        self.Ch2xCh2.configure(background="#f9f9f9")
        self.Ch2xCh2.configure(disabledforeground="#a3a3a3")
        self.Ch2xCh2.configure(font=font10)
        self.Ch2xCh2.configure(foreground="#000000")
        self.Ch2xCh2.configure(highlightbackground="#d9d9d9")
        self.Ch2xCh2.configure(highlightcolor="black")
        self.Ch2xCh2.configure(variable = self.Ch2ACFVar)
        self.Ch2xCh2.pack()
        self.Ch2xCh2.place(relx=0.55, rely=0.60,height=30, relwidth=0.3)

        #OK and Cancel buttons
        self.OKbutton = Button(top, text="OK", command=self.updateData)
        self.OKbutton.configure(activebackground="#f9f9f9")
        self.OKbutton.configure(activeforeground="black")
        self.OKbutton.configure(background="#f9f9f9")
        self.OKbutton.configure(disabledforeground="#a3a3a3")
        self.OKbutton.configure(font=font10)
        self.OKbutton.configure(foreground="#000000")
        self.OKbutton.configure(highlightbackground="#d9d9d9")
        self.OKbutton.configure(highlightcolor="black")
        self.OKbutton.pack()
        self.OKbutton.place(relx=0.17, rely=0.83,height=30, relwidth=0.25)

        self.cancelButton = Button(top, text="Cancel", command=self.cancelParams)
        self.cancelButton.configure(activebackground="#f9f9f9")
        self.cancelButton.configure(activeforeground="black")
        self.cancelButton.configure(background="#f9f9f9")
        self.cancelButton.configure(disabledforeground="#a3a3a3")
        self.cancelButton.configure(font=font10)
        self.cancelButton.configure(foreground="#000000")
        self.cancelButton.configure(highlightbackground="#d9d9d9")
        self.cancelButton.configure(highlightcolor="black")
        self.cancelButton.pack()
        self.cancelButton.place(relx=0.52, rely=0.83,height=30, relwidth=0.35)

               

    def validateNumTrials(self,*args):
        y  = self.maxTrialStr.get()
        print(y)
        if y[0] in "0123456789":
            return True
        else:
            print("Invalid Entry")
            self.maxTrialStr.set("1")
            return False

    def cancelParams(self,*args):
        self.newData = "No"
        self.acqDur = 0
        self.maxNumTrials = 0
        self.correlations = [0,0,0,0]
        try:
            root.destroy()
        except:
            destroy_OptionWindow()
        

    def updateData(self,*args):
        self.newData = "Yes"
        self.acqDur = int(self.timeVar.get())
        self.maxNumTrials = int(self.maxTrialStr.get())
        self.correlations[0] = self.Ch1ACFVar.get()
        self.correlations[1] = self.Ch1xCh2Var.get()
        self.correlations[2] = self.Ch2xCh1Var.get()
        self.correlations[3] = self.Ch2ACFVar.get()
        try:
            root.destroy()
        except:
            destroy_OptionWindow()
        


        
if __name__ == '__main__':
    vp_start_gui()
