import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import time

#Todo Add Threading
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
    startTime = time.time()
    results = multiTauTStamp(ch1,ch1,m=8,maxTau=2000000)
    endTime = time.time()
    print("Time Elapsed: " + str(endTime-startTime))
    cf = results[0]
    bins = results[1]
    mask = np.greater_equal(bins,2)
    plt.semilogx(bins[mask]*0.5e-6,cf[mask],**{'linestyle':'none','marker':'o'})
    plt.show()

def multiTauTStamp(x,y,m=8,maxTau=100000000,normalize=True):
    cf = np.zeros(1)
    bins = createBins(m=m,maxTau=maxTau)
    N = np.maximum(np.max(x),np.max(y))
    muX = len(x)/np.max(x)
    muY = len(y)/np.max(y)
    norm = N-bins#biased normalization 
    for j in range(np.uint32(np.floor((len(bins)-1)/m))):
        startIdx = np.round(bins[j*m+1]/2**j)-1
        temp = simpleCorr(x,y,m,startIdx)/2**j
        cf = np.concatenate([cf,temp])
        x = rebin(x)
        y = rebin(y)
    if normalize==True:
        cf = cf/(muX*muY*norm)-1
    return(cf,bins,muX)

def multiTauTStampMP(x,y,m=8,maxTau=100000000,normalize='True'):
    bins = createBins(m=m,maxTau=maxTau)
    N = np.maximum(np.max(x),np.max(y))
    muX = len(x)/np.max(x)
    muY = len(y)/np.max(y)
    norm = N-bins #unbiased normalization
    pool = mp.Pool(processes = 4)
    cf = [pool.apply(simpleCorr, args = (rebin(x,factor=2**j),rebin(y,factor=2**j),np.uint32(np.round(bins[j*m+1]/2**j)-1,normFactor=2**j))) for j in range(np.uint32(np.floor((len(bins)-1)/m)))]
   # for j in range(np.uint32(np.floor((len(bins)-1)/m))):
     # startIdx = np.round(bins[j*m+1]/2**j)-1
   #     temp = simpleCorr(x,y,m,startIdx)/2**j
   #     cf = np.concatenate([cf,temp])
   #     x = rebin(x)
   #     y = rebin(y)
    print(cf)
    if normalize=='True':
        cf = cf/(muX*muY*norm)-1
    return(cf,bins,muX)

def meanStdFromStamps(x):
    xx = Counter(x)
    X = np.unique(x)
    N = np.max(x)
    sse = 0
    meanX = len(x)/N
    for j in range(len(X)):
        sse = sse+(xx[X[j]]-meanX)**2
    stdX = np.sqrt(sse/(N-1))
    return(meanX,stdX)
    
def createBins(m=8,maxTau=100000000):
    bins = np.zeros(1)
    startIdx = 0
    n = 0
    while np.max(bins)<maxTau:
        temp = np.linspace(startIdx+2**n,m*2**n+startIdx,m)
        startIdx = np.max(temp)
        bins = np.concatenate([bins,temp])
        n = n+1
    return(bins)
        
def simpleCorr(x,y,m=8,startIdx=0,normFactor=1):
    cf = np.zeros(m)
    #X = Counter(x) #Get counts of unique values
    X,CountX = np.unique(x,return_counts = True)
    for j in range(1,m+1):
        yy = y+j+startIdx #shifted matrix
        Y,CountY = np.unique(yy,return_counts = True)
        Z,idxX,idxY = np.intersect1d(X,Y,return_indices = True)
        cf[j-1] = np.dot(CountX[idxX],CountY[idxY])/normFactor
    return(cf)

def rebin(x,factor = 2):
    #rebin by factor of x
    return(np.uint32(x/factor))


if __name__ == '__main__':
    fullTest = 1
    if fullTest:
        runTest()
    else: 
        A = np.array([1, 2, 3, 5, 5, 7, 7, 8, 8,9,10,11,11,11,12,15,16])        
        a = np.zeros(np.max(A)+1)
        for j in range(len(A)):
            a[A[j]] = a[A[j]]+1
        results = multiTauTStamp(A,A,m=16,maxTau = 1000)
        mask = np.less_equal(results[1],50)
        bins = np.linspace(0,np.max(A)-1,np.max(A))
        plt.plot(bins,results)
        temp = np.correlate(a,a,mode = 'Full')
        plt.plot(bins,temp[np.uint32((len(temp)-1)/2):len(temp)-1])
        print(results)
        print(temp[np.uint32((len(temp)+1)/2):len(temp)-1])
        plt.xlim([1,50])
        plt.show()
    
