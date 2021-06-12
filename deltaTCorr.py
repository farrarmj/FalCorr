import numpy as np
import io
import matplotlib.pyplot as plt


def deltaTsFromFile(file,dataType=np.uint16):
    #Extract data from bin file
    rawWrites = np.fromfile(file,dtype=dataType)
    ch1 = rawWrites[0:len(rawWrites):2]
    ch2 = rawWrites[1:len(rawWrites):2]
    
    #Remove blanks
    mask = np.less(ch1,65535)
    ch1 = ch1[mask]
    mask = np.less(ch2,65535)
    ch2 = ch2[mask]
    return(ch1,ch2)

def autocorrelationFullRes(x,maxTau=1000000,normalize = False):
    Bins = np.linspace(1,maxTau,maxTau) #time bins
    ACF = np.zeros(maxTau) #ACF 
    delays = np.zeros(maxTau,dtype = np.uint64) #Delay vector
    for j in range(len(x)):
        delays[1:len(delays)-1] = delays[0:len(delays)-2]
        delays[0] = 0
        delays = delays+x[j]
        mask = np.greater_equal(delays,maxTau)
        delays[mask] = 0
        ACF[delays] = ACF[delays]+1 #update ACF
    return (ACF,Bins)

def runTest():
    testFile = r'C:\Users\mfarrar.MESSIAH\Documents\FCS_Measurements\20180727\Sample7_TetraspeckDualEx_1to100_ShortAcq_Trial_1_Trial_1.bin'
    deltaTs = deltaTsFromFile(testFile,dataType =np.uint16)
    ch1 = deltaTs[0]
    ch2 = deltaTs[1]
    results = autocorrelationFullRes(ch1,maxTau = 1000000)
    ACF = results[0]
    bins = results[1]
    print(ACF[5])
    mask = np.greater_equal(bins,2)
    plt.semilogx(bins[mask],ACF[mask])
    plt.show()
    

if __name__ == '__main__':
    runTest()
