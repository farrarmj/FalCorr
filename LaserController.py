from tkinter import *
import serial
import time
import struct
import connectToSerial as ardSer

def vp_start_gui():
    global w, root
    root = Tk()
    top =laserController(root)
    root.mainloop()
    w = None
def create_New_laserController(root):
    '''Starting point when module is imported by another program.'''
    rt = root
    w = Toplevel (root)
    top = laserController(w)
    return (w, top)

def destroy_New_Toplevel():
    global w
    w.destroy()
    w = None


class laserController:
    def __init__(self, top = None):
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

        top.geometry("175x100+154+102")
        top.title("Laser Power Controller")
        top.configure(background="#d9d9d9")
        top.configure(highlightbackground="#d9d9d9")
        top.configure(highlightcolor="black")
        #Frame.__init__(self)
        #frame = Frame(master)
        #frame.pack()
        #frame.tk_focusFollowsMouse()
        #master.title("Laser Power Controller")

        self.ser = ardSer.arduinoSerial();
        
        self.runStatus =1;
        self.idleStatus = 1;
       
        #create top level menu
        self.menubar = Menu(top)
        top.configure(menu = self.menubar)
        #File Menu
        #menu= Menu(self.menubar,tearoff=0)
     ##   self.menubar.add_cascade(label="File", menu=menu)
       # menu.add_command(label="Exit",command=destroy_New_Toplevel())
    
         
        #Run Menu
        menu = Menu(self.menubar,tearoff=0)
        self.menubar.add_cascade(label="Run", menu=menu)
        menu.add_command(label="Run",command=self.RunLaser)
        menu.add_command(label="Idle",command=self.idleLaser)
        menu.add_command(label="Off",command=self.laserOff)
        
        #try:
        #    self.master.config(menu=self.menubar)
        #except AttributeError:
        #    print("Attribute Error")
            # master is a toplevel window (Python 1.4/Tkinter 1.63)
        #    self.master.tk.call(master, "config", "-menu", self.menubar)

        #self.canvas = Canvas(self, bg="white", width=250, height=25,
            #                 bd=0, highlightthickness=0)
        #self.canvas.pack()

        #Power Setting TO Arduino
        self.userPwr = Label(top,text = "Set Power (%)")
        self.userPwr.grid(row=0,column=0)
        self.slider = Scale(top, from_=0, to=100, orient=HORIZONTAL,command=self.setText)
        self.slider.grid(row=1,column=0)

        self.v = StringVar()
        vcmd = (top.register(self.setSlider),
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.power = Entry(top,width = 3,validate = 'focus',validatecommand=vcmd, textvariable=self.v)
        self.v.set("0")
        self.power.grid(row=1,column=1)
        self.power.after_idle(self.power.config,{'validate':'focus'})

        #Power Readout FROM Arduino
        #self.P = StringVar()
        #self.pwrReadout = Label(frame,text = "Laser Power (mW)")
        #self.pwrReadout.grid(row=2,column=0)
        #self.laserPower = Entry(frame,width=3,textvariable=self.P)
        #self.laserPower.grid(row=2,column=1)

        
        #Radio Buttons Status Indicators
        self.LaserOn = Radiobutton(top,text = "Running",variable=self.runStatus,value=1,state = DISABLED)
        self.LaserOn.grid(row=3,column=0)
        self.laserIdle = Radiobutton(top,text = "Idling",variable=self.idleStatus,value=2,state = DISABLED)
        self.laserIdle.grid(row=3,column=1)
        self.laserIdle.select()
    
    #Callback Definitions

    def setText(self,val): #Make text match slider, update Arduino
        self.v.set(str(val))
 #       self.ser.write(struct.pack('>B', int(val)+50)) –> already under text eval
        return None

    def setSlider(self, action, index, value_if_allowed, #Make slider match text, update Arduino
                       prior_value, text, validation_type, trigger_type, widget_name):
        if text in '0123456789.-+':
            try:               
                if int(value_if_allowed)>=0 and int(value_if_allowed)<=100:
                    self.slider.set(int(value_if_allowed))
                    self.ser.write(struct.pack('>B', int(value_if_allowed)+50))
                    #print(int(value_if_allowed)+50)
                    #time.sleep(0.1) #Allow time for update
                    #self.ser.write(struct.pack('>B', 10))#Request true power update
                    #time.sleep(0.1) #Pause for answer
                    #a=self.ser.read(size=1) #Read answer
  #                  self.P.set(str (int.from_bytes(a,byteorder='big')))#Update Controller
                    return True
                else:
                    self.v.set(str(self.slider.get()))
                    self.power.after_idle(lambda: self.power.config(validate='focus'))
                    return None
            except ValueError:
                self.v.set(str(self.slider.get()))
                self.power.after_idle(lambda: self.power.config(validate='focus'))
                return None
            
        else:
            self.v.set(str(self.slider.get()))
            self.power.after_idle(lambda: self.power.config(validate='focus'))
            return None

    def idleLaser(self):
        #print("Idling")
        self.ser.write(struct.pack('>B', 2))
        self.LaserOn.deselect()
        self.laserIdle.select()
        
            
    def RunLaser(self):
        #print("Running")
        self.ser.write(struct.pack('>B', 3))
        self.LaserOn.select()
        self.laserIdle.deselect()
 
                           
    def laserOff(self):
        #print("Laser Off")
        self.ser.write(struct.pack('>B', 1))
        self.LaserOn.deselect()
        self.laserIdle.deselect()


if __name__ == '__main__':
    vp_start_gui()

