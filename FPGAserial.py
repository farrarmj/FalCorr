#This module creates a FPGA object based on the Artyboard Xilinx Artix 7
#programmed with a TDC that measures a difference in time stamps
import serial
import serial.tools.list_ports
import struct
import numpy as np
import io
import time
from threading import Thread
def openFPGA(mode = None):
    #Initialize serial port
   
    ser = serial.Serial()           #Serial port object
    ser.baudrate =  8000000         #set baud rate
    ser.set_buffer_size(rx_size=250000000,tx_size=4096)             
    ser.bytesize = serial.EIGHTBITS     #Set byte size
    ser.parity = serial.PARITY_NONE     #Set number of parity bits
    ser.stopbits = serial.STOPBITS_ONE  #Set stopbits number 1
    ser.timeout = 3
    ser.write_timeout=5
    ports = serial.tools.list_ports.comports()
    if mode == 'DLS':             #DLS FPGA
        for p in ports:
            if " SER=210319756340B" in p[2]:
                ser.port = p[0]
        ser.open()
    elif mode == 'FCS':           #FCS FPGA
        for p in ports:
            if " SER=210319798825B" in p[2]:
                ser.port = p[0]
        ser.open()
    else:
        ser.port = ''
    fpga = serialFPGA(ser)
    return(fpga)

class serialFPGA:
    def __init__(self, ser):
        self.ser = ser
        self.commandList = {"Reset":struct.pack('<B',0),
                            "Start Acq":struct.pack('<B',10),
                            "LED On":struct.pack('<B',20),
                            "LED Off":struct.pack('<B',30),
                            "ACQ_25":struct.pack('<B',99),
                            "ACQ_5":struct.pack('<B',100),
                            "ACQ_1":struct.pack('<B',101),
                            "ACQ_3":struct.pack('<B',102),
                            "ACQ_10":struct.pack('<B',103),
                            "ACQ_30":struct.pack('<B',104),
                            "ACQ_100":struct.pack('<B',105),
                            "ACQ_300":struct.pack('<B',106),
                            "ACQ_1000":struct.pack('<B',107),
                            "ACQ_inf":struct.pack('<B',110),
                            "STOP_ACQ":struct.pack('<B',199)
                            }
        self.running=0
        #Blink LED 3 times
        if not ser.port == '':
            for j in range(0,3):
                self.ser.write(self.commandList.get("LED On"))
                time.sleep(0.5)
                self.ser.write(self.commandList.get("LED Off"))
                time.sleep(0.5)
        
    def getCountRate(self,prevCountRate,dataType=np.uint8):
        bytesToRead = 500 #read 510 bytes       
        b = self.ser.read(bytesToRead) #read 500 bytes
        if dataType == np.uint8 and self.running:
            #assumes 8-bit time stamp differences with 1 µs precision
            elapsedTime = sum(list(b))
            if elapsedTime:
                countRate = len(b)/elapsedTime*1000 #count rate in kHz
            else:
                countRate = prevCountRate
        elif dataType == np.uint16 and self.running:
            #assumes 16-bit time stamp differences with 0.125 us precision
            fmt = str(np.uint16(bytesToRead/2))+'H'
            deltaT = struct.unpack(fmt,b) #interpret at 16 bits
            elapsedTime = sum(deltaT)
            if elapsedTime:
                countRate = len(b)/2/(0.125*elapsedTime)*1000 #count rate in kHz
            else:
                countRate = prevCountRate
        else:
            countRate = prevCountRate
        return(countRate)

    def getCountRateDualChannel(self,dataType=np.uint16,timeScale=0.5e-6):
        countsCh1 = 0
        countsCh2 = 0
        elapsedTimeCh1 = 0
        elapsedTimeCh2 = 0
        self.ser.reset_input_buffer() #clear all previous reads
        bytesToRead = 4000 #Read all bytes in buffer
        self.startAcq() #start read
        B = self.ser.read(bytesToRead)
        self.stopAcq()
        self.ser.reset_input_buffer()
        if dataType == np.uint8:
            #assumes 8-bit time stamp differences with 1 µs precision
            b1 = np.array(list(b[0:len(B):2])) #ch1 stamps are even
            b2 = np.array(list(b[1:len(B):2])) #ch2 stamps are odd
            mask1 = np.not_equal(b1,255) #remove non-data points
            mask2 = np.not_equal(b2,255) #remove non-data points
            b1 = b1[mask1]
            b2 = b2[mask2]
            countsCh1 = len(b1)
            elapsedTimeCh1 = np.sum(b1)
            countsCh2 = len(b2)
            elapsedTimeCh2 = np.sum(b2)
        elif dataType == np.uint16:
            #assumes 16-bit time stamp differences with 0.5 us precision
            fmt = str(np.uint16(len(B)/2))+'H'
            deltaT = struct.unpack(fmt,B) #interpret as 16-bit-numbers
            b1 = np.array(list(deltaT[0:len(B):2])) #ch1 stamps are even
            b2 = np.array(list(deltaT[1:len(B):2])) #ch2 stamps are odd
            mask1 = np.not_equal(b1,65535) #remove non-data points
            mask2 = np.not_equal(b2,65535) #remove non-data points
            b1= b1[mask1]
            b2 = b2[mask2]
            countsCh1 = len(b1)
            elapsedTimeCh1 = np.sum(b1)
            countsCh2 = len(b2)
            elapsedTimeCh2 = np.sum(b2)
        if elapsedTimeCh1 or elapsedTimeCh2:
            elapsedTime = max(elapsedTimeCh1,elapsedTimeCh2)
            countRateCh1 = countsCh1/(timeScale*elapsedTime)/1000
            countRateCh2 = countsCh2/(timeScale*elapsedTime)/1000
        else:
            countRateCh1 = np.nan
            countRateCh2 = np.nan
        return(countRateCh1,countRateCh2)


    def setAcqTime(self,acqTime):
        if np.isnan(acqTime):
            commandStr = "STOP_ACQ"
        else:
            commandStr = "ACQ_"+str(acqTime)
        if commandStr in self.commandList:
            self.ser.write(self.commandList.get(commandStr))
    
    def startAcq(self): #start acqusition signal
        self.running=1
        self.ser.write(self.commandList.get("Start Acq"))

    def dataWaiting(self):
        A = self.ser.in_waiting
        return(A)

    def read(self,bytesToRead):
        return(self.ser.read(bytesToRead))
        

    def stopAcq(self):
        self.running=0
        self.ser.write(self.commandList.get("Reset"))
        self.ser.reset_input_buffer()

    def closeFPGA(self):
        self.ser.close()

if __name__ == '__main__':
     fpga = openFPGA()
     fpga.dataWaiting()
     fpga.closeFPGA()
