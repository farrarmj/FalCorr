import numpy as np
import scipy.sparse as sprs
import multipletau as mt
import matplotlib.pyplot as plt
import io
import os
import queue
import time
import sys

def runTest():
    #read file
    testFile = r'C:\Users\mfarrar.MESSIAH\Documents\FCS_Measurements\20180727\Sample7_TetraspeckDualEx_1to100_ShortAcq_Trial_1_Trial_1.bin'
    rawWrites = np.fromfile(testFile,dtype=np.uint16)
    ch1 = rawWrites[0:len(rawWrites):2]
    ch2 = rawWrites[1:len(rawWrites):2]
    
    #Remove blanks
    mask = np.less(ch1,65535)
    ch1 = ch1[mask]
    mask = np.less(ch2,65535)
    ch2 = ch2[mask]

    #Convert to time stamps
    ch1 = np.cumsum(ch1,dtype= np.uint32)
    ch2 = np.cumsum(ch2,dtype= np.uint32)

    #Convert from Delta t's to bins
    ch1Bins = tStampsToBinFills(ch1)
    ch2Bins = tStampsToBinFills(ch2)
    #cutoff = np.minimum(np.size(ch1Bins),np.size(ch2Bins))
    cutoff = 200000000
    ch1Bins = ch1Bins[0][0:cutoff]
    ch2Bins = ch2Bins[0][0:cutoff]

    #Calculate ACF/CCF
    ACF = mt.autocorrelate(ch1Bins, m=8, deltat=1, normalize=True, copy=True)#, dtype=None, compress='average', ret_sum=False)
   # acf = mt.correlate(ch1Bins,ch1Bins,m=8,deltat =1, normalize = True,copy = True)
   # CCF12 = mt.correlate(ch1Bins,ch2Bins, m=8, deltat=1, normalize=True, copy=True)#, dtype=None, compress='average', ret_sum=False)
   # CCF21 = mt.correlate(ch2Bins,ch1Bins,m=8,deltat = 1, normalize = True,copy = True)
    
    #Make plto for ACF
    fig = plt.figure
    plt.subplot(211)
    temp = ACF.flatten()
    Bins = temp[0:len(temp):2]*1e-6
    CF = temp[1:len(temp):2]
    mask = np.greater_equal(Bins,1e-5) & np.less_equal(Bins,1)
    plt.semilogx(Bins[mask],CF[mask])
    #temp = acf.flatten()
   # Bins = temp[0:len(temp):2]*1e-6
   # CF = temp[1:len(temp):2]
   # mask = np.greater_equal(Bins,1e-5) & np.less_equal(Bins,1)
   # plt.semilogx(Bins[mask],CF[mask])
    
        
    #Makeplot for CCF
    #plt.subplot(212)
    #temp = CCF12.flatten()
    #Bins = temp[0:len(temp):2]*1e-6
    #CF = temp[1:len(temp):2]
    #mask = np.greater_equal(Bins,1e-5) & np.less_equal(Bins,1)
    #plt.semilogx(Bins[mask],CF[mask])
    #temp = CCF21.flatten()
    #Bins = temp[0:len(temp):2]*1e-6
    #CF = temp[1:len(temp):2]
    #mask = np.greater_equal(Bins,1e-5) & np.less_equal(Bins,1)
    #plt.semilogx(Bins[mask],CF[mask])

    plt.show()


def tStampsToBinFills(data):
    bins = np.zeros([1,np.uint32(np.max(data)+1)],dtype=np.float)
    for j in range(len(data)):
        bins[0][data[j]] = bins[0][data[j]]+1
    return(bins)


if __name__ == '__main__':
    runTest()

    
