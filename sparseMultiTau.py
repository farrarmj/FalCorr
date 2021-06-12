import numpy as np
import matplotlib.pyplot as plt
import io

def runTest():
    #read file
    testFile = r'C:\Users\mfarrar.MESSIAH\Documents\FCS_Measurements\20180727\Sample7_TetraspeckDualEx_1to100_LongAcq_Trial_1.bin'
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
    ch2Bins = tStampsToBinFill
    cutoff = np.minimum(np.size(ch1Bins),np.size(ch2Bins))
    ch1Bins = sprs.coo_matrix(ch1Bins[0][0:cutoff])
    ch2Bins = sprs.coo_matrix(ch2Bins[0][0:cutoff])

    #Calculate ACF/CCF
    

def tStampsToBinFills(data):
    bins = np.zeros([1,np.uint32(np.max(data)+1)],dtype=np.float)
    for j in range(len(data)):
        bins[0][data[j]] = bins[0][data[j]]+1
    return(bins)

def simpleCorr(x,y,m=8,startIdx = 0):
    x*y.transpose()


if __name__ == '__main__':
    runTest()

    
