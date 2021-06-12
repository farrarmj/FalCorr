import scipy.optimize as curvefit
import numpy as np
import myCorr
import os
import io

class scopeFit: 
    def __init__(self,wavelength):
        if wavelength ==488:
            configVals = parseConfig()
            self.wxy = configVals[0]
            self.a=configVals[1]
        elif wavelength ==543:
            configVals = parseConfig()
            self.wxy = configVals[2]
            self.a = configVals[3]
        else:
            self.wxy = np.NAN
            self.a = np.NAN
            
    #Calibration curve (simple monomodal)
    def calibrationCurve(self,x,G0,GInf,tauD,A):
        return(GInf + G0/(1+x/tauD)/(1+A**(-2)*(x/tauD))**0.5)

    #fit calibration curve
    def calFit(self,x = None,y = None):
        p0 = [np.max(y),0,1e-4,5]#initial guess at parameters
        maxP = ([0,-1,0.5e-6,0],[10*np.max(y),1,1,100])
        params,pconv = curvefit.curve_fit(f=self.calibrationCurve,xdata = x,ydata = y,p0 = p0,bounds = maxP)
        return(params)

    #Simple one particle fit w/o triplet
    def simpleMonodisperse(self,x,G0,GInf,tauD):
        return(GInf + G0/(1+x/tauD)/(1+self.a**(-2)*(x/tauD))**0.5)

    #Simple one particle fit w/triplet correction
    def tripletMonodisperse(self,x,G0,GInf,F,tauD,tauF):
        return(GInf+G0*(1-F+F*np.exp(-x/tauF))/((1-F)*(1+(x/tauD))*(1+self.a**(-2)*(x/tauD))**0.5))

    #anomalous diffusion w/o triplet
    def simpleAnomalous(self,x,G0,GInf,tauD,alpha):
        return(GInf + G0/(1+(x/tauD)**alpha)/(1+self.a**(-2)*(x/tauD)**alpha)**0.5)

    #anomalous diffusion w/triplet correction
    def tripletAnomalous(self,x,G0,GInf,F,tauD,alpha,tauF):
        return(GInf+G0*(1-F+F*np.exp(-x/tauF))/((1-F)*(1+(x/tauD))*(1+self.a**(-2)*(x/tauD))**0.5))

    #Simple two particle fit w/o triplet
    def simpleBimodal(self,x,G1,G2,GInf,tauD1,tauD2):
        A = G1/(1+(x/tauD1))/(1+self.a**(-2)*(x/tauD1))**0.5
        B = G2/(1+(x/tauD2))/(1+self.a**(-2)*(x/tauD2))**0.5
        return(GInf+A+B)

    #Simple two particle fit w/triplet correction
    def tripletBimodal(self,x,G1,G2,GInf,F,tauD1,tauD2,tauF):
        A = G1*(1-F+F*np.exp(-x/tauF))/(1-F)/(1+(x/tauD1))/(1+self.a**(-2)*(x/tauD1))**0.5
        B = G2*(1-F+F*np.exp(-x/tauF))/(1-F)/(1+(x/tauD2))/(1+self.a**(-2)*(x/tauD2))**0.5
        return(GInf+A+B)


    #Determine associated hydrodynamic diameter from fit parameters                                            
    def hydroDiam(self,tauD,Temp=295,eta=8.90e-4):
        kb = 1.38064852e-23 #Boltzmann constant
        wxy = self.wxy*1e-6 #convert from microns
        Dt = wxy**2/(4*tauD)
        Dh= kb*Temp/(3*np.pi*eta*Dt)
        return(Dh)


    def getHydroDiam(self,fitType='simpleMonodisperse',x=None,y=None,Temp=295,eta=8.90e-4):
        if fitType=="simpleMonodisperse":
            p0 = [np.max(y),0,1e-3] #initial guess at parameters
            maxP = ([0,-1,1e-6],[10*np.max(y),1,1]) #constraining fit parameters
            results = curvefit.curve_fit(f=self.simpleMonodisperse,xdata=x,ydata=y,p0=p0,bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD = fitParams[2] #pull out time constant
            Dh1 = self.hydroDiam(tauD,Temp,eta) #solve for hydrodynamic diameter
            Dh2 = np.NAN
            alpha = 0.5
        elif fitType=="tripletMonodisperse":
            p0 = [np.max(y),0,0.1,1e-3,1e-6] #intial guess at parameters
            maxP = ([0,-0.5,0,0.5e-6,1e-7],[10*np.max(y),0.5,1,1,1e-5])
            results = curvefit.curve_fit(self.tripletMonodisperse,xdata=x,ydata=y,p0=p0,bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD = fitParams[3] #pull out time constant
            Dh1 = self.hydroDiam(tauD,Temp,eta) #solve for hydrodynamic diameter
            Dh2 = np.NAN
            alpha = 0.5
        elif fitType =="simpleBimodal":
            p0 = [np.max(y)/2,np.max(y)/2,0,1e-3,1e-3] #initial guess at parameters
            maxP = ([0,0,-1,1e-6,1e-6],[5*np.max(y),5*np.max(y),1,1,1])
            results = curvefit.curve_fit(f = self.simpleBimodal,xdata = x,ydata = y, p0 = p0, bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD1 = fitParams[3] #pull out time constants
            tauD2 = fitParams[4]
            Dh1 = self.hydroDiam(tauD1,Temp,eta) #solve for hydrodynamic diameters
            Dh2 = self.hydroDiam(tauD2,Temp,eta)
            alpha = 0.5
        elif fitType=="tripletBimodal":
            p0 = [np.max(y)/2,np.max(y)/2,0,0.1,1e-3,1e-3,1e-6] #intial guess at parameters
            maxP = ([0,0,-1,0,5e-7,5e-7,1e-7],[5*np.max(y),5*np.max(y),1,0.5,1,1,1e-5])
            results = curvefit.curve_fit(f=self.tripletBimodal,xdata=x,ydata=y,p0=p0,bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD1 = fitParams[4] #pull out time constants
            tauD2 = fitParams[5]
            Dh1 = self.hydroDiam(tauD1,Temp,eta) #solve for hydrodynamic diameters
            Dh2 = self.hydroDiam(tauD2,Temp,eta)
            alpha = 0.5
        elif fitType=="simpleAnomalous":
            p0 = [np.max(y),0,1e-3,0.5] #intial guess at parameters
            maxP = ([0,-1,1e-6,0],[10*np.max(y),1,1,5])
            results = curvefit.curve_fit(f=self.simpleAnomalous,xdata=x,ydata=y,p0=p0,bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD = fitParams[2] #pull out time constant
            Dh1 = self.hydroDiam(tauD,Temp,eta) #solve for hydrodynamic diameter
            Dh2 = np.NAN
            alpha = fitParams[3]
        elif fitType == "tripletAnomalous":
            p0 = [np.max(y),0,0.1,1e-3,0.5,1e-6] #intial guess at parameters
            maxP = ([0,-1,0,5e-7,0,1e-7],[10*np.max(y),1,1,1,5,1e-5])
            results = curvefit.curve_fit(f=self.tripletAnomalous,xdata=x,ydata=y,p0=p0,bounds = maxP) #fit curve
            fitParams = results[0] #fit parameters
            tauD = fitParams[3] #pull out time constant
            Dh1 = self.hydroDiam(tauD,Temp,eta) #solve for hydrodynamic diameter
            Dh2 = np.NAN
            alpha = fitParams[4]
        else:
            fitParams = np.NAN
            Dh1 = np.NAN
            Dh2 = np.NAN
            alpha = np.NAN
        return(fitParams,Dh1,Dh2,alpha,self.wxy,self.a)

#block to read parameters from configuration file
def parseConfig():
    path = os.getenv('ProgramFiles(x86)')
    path = os.path.join(path,'FalCorr')
    configFile = os.path.join(path,'config.txt')
    fid = io.open(configFile,mode = 'r')
    configVals = np.zeros([4,1])
    for j in range(0,4):
        configStr = fid.readline()
        vals = configStr.split()
        configVals[j] = float(vals[1])
    fid.close()
    return(configVals)    
    
#Determine concentration from N and config parameters
def measureConc(G0,wavelength):
    configVals = parseConfig()
    if wavelength ==488:
        wxy = configVals[0]
        a = configVals[1]
    elif wavelength ==543:
        wxy = configVals[2]
        a = configVals[3]
    else:
        wxy = np.NAN
        a =np.NAN
    Avo =6.0221409 #Avogadros's number less 10^23
    N = 1/G0
    V = a*(wxy**3)*(np.pi)**1.5 #Calculate focal volume in cubic microns
    conversion_factor =10 #divide by 1e23 for Avo to get tomols,divide by 10^-15 for concentrationin mol/L, multiply by 1e9 to get nMol: overall 10 
    conc = N/Avo/V*10 #concentration in mol
    return(conc)

if __name__ == '__main__':
    uScope = scopeFit(488)
    print("wxy: " + str(uScope.wxy))
    print("a: " + str(uScope.a))
