import numpy as np
import io
import multiTauTStamps as mtT

def timeStampsfromDifferences2Chan(file,dataType=np.uint16,cumSum = True):
    rawWrites = np.fromfile(file,dtype=dataType)
    x = rawWrites[0:len(rawWrites):2]
    y = rawWrites[1:len(rawWrites):2]
    
    #Remove blanks
    mask = np.less(x,65535)
    x = x[mask]
    mask = np.less(y,65535)
    y = y[mask]
    if cumSum:
        x = np.cumsum(x,dtype= np.uint64)
        y = np.cumsum(y,dtype= np.uint64)
    return(x,y)

def getPCHs(file,dataType = np.uint16,intBins=400,maxCounts=10):
    x,y = timeStampsfromDifferences2Chan(file,dataType,cumSum = True)
    if len(x):
        xBin = np.arange(0,np.max(x),intBins) #generate windows
        timeDist1 = np.histogram(x,xBin,density = False) #get counts in intBins
        #Generate PCH
        PCH1 = np.histogram(timeDist1[0],np.arange(0,maxCounts,1),density = True)
    else:
        PCH1 = ([np.nan],[np.nan])
    if len(y):
        yBin = np.arange(0,np.max(y),intBins) #generate windows
        timeDist2 = np.histogram(y,yBin,density = False) #get counts in intBins
        #Generate PCH
        PCH2 = np.histogram(timeDist2[0],np.arange(0,maxCounts,1),density = True)
    else:
        PCH2 = ([np.nan],[np.nan])
    #Generate PCHs
    return(PCH1,PCH2)

def timeStampsToBinFills(data):
    bins = np.zeros([1,np.uint64(np.max(data)+1)],dtype=np.float)
    for j in range(len(data)):
        bins[0][data[j]] = bins[0][data[j]]+1
    return(bins)

def multiTauCFfromDeltas(file,dataType=np.uint16,corrType =0):
 #corrType options:
    #0: Ch1 ACF
    #1: Ch1 x Ch2
    #2: Ch2 x Ch1
    #3: Ch2 ACF

    #Take delta ts to time stamps
    tStamps = timeStampsfromDifferences2Chan(file,dataType)
    ch1 = tStamps[0]
    ch2 = tStamps[1]

    
    #Compute Appropriate Correlation
    if corrType==0:
        results = mtT.multiTauTStamp(ch1,ch1, m=8, maxTau = 100000000, normalize=True)
        #insert ambient correlation for Ch1 here
        Gnorm= afterPulseCorrection(results[0],results[2],chan=1)
    elif corrType==1:
        results = mtT.multiTauTStamp(ch1,ch2, m=8, maxTau = 100000000, normalize=True)
        Gnorm = results[0]
    elif corrType==2:
        results = mtT.multiTauTStamp(ch2,ch1, m=8, maxTau = 100000000, normalize=True)
        Gnorm = results[0]
    elif corrType==3:
        #insert ambient correlation for Ch2 here
        results = mtT.multiTauTStamp(ch2,ch2, m=8, maxTau = 100000000, normalize=True)
        Gnorm =afterPulseCorrection(results[0],results[2],chan=2)

    bins = results[1]
    return(Gnorm,bins)

def afterPulseCorrection(acf,muX,chan=1):
    if chan==1:
        file = r'ambientLight_Average_Ch1.npz'
    else:
        file = r'ambientLight_Average_Ch2.npz'
    data = np.load(file)
    APCF = data['CF']
    N = min(len(APCF),len(acf))
    acf = acf[0:N]-APCF[0:N]/muX
    return(acf)

def getCountRate(file, dataType = np.uint16):
    ch1,ch2 = timeStampsfromDifferences2Chan(file,dataType,cumSum = False)
    if len(ch1):
        countRateCh1 = len(ch1)/np.sum(ch1)
    else:
        countRateCh1 = np.nan
    if len(ch2):
        countRateCh2 = len(ch2)/np.sum(ch2)
    else:
        countRateCh2 = np.nan
    return(countRateCh1,countRateCh2)

if __name__ == '__main__':
    testFile = r'C:\Users\mfarrar.MESSIAH\Documents\FCS_Measurements\20180727\Sample7_TetraspeckDualEx_1to100_ShortAcq_Trial_1_Trial_1.bin'
    #countRates = getCountRate(testFile)
    #print(countRates[0]/0.5e-6/1000)
    PCHs =  getPCHs(file=testFile,dataType = np.uint16,intBins= 100,maxCounts=20)
    print(PCHs[0][0])
    print(PCHs[1][0])
