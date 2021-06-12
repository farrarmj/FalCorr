import scipy.optimize as curvefit
import numpy as np

class myLinFit:
    
    def __init__(self):
        self.b=3
        
    def linearFunc(self,x,m):
        return(m*x+self.b)
       



if __name__ == '__main__':
    x = np.linspace(0,20,21)
    y = 2*x +3
    fitter = myLinFit()
    #print(fitter.linearFunc(2,3))
    popt,pcov = curvefit.curve_fit(f = fitter.linearFunc,xdata = x,ydata = y)
    print("m:\t" + str(popt[0]) +"\n")
