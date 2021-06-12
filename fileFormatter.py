import pandas as pd
import numpy as np
from tkinter.filedialog import askopenfilenames

def npzToFormat(NPZfiles = ''):
        #Prompt for file names if none provided
        if not NPZfiles:
            NPZfiles = askopenfilenames(title = "Select NPZ Files",filetypes = (("NPZ Files","*.npz"),("all files","*.*")))
        
        for j in range(0,len(NPZfiles)):
            data = np.load(NPZfiles[j])

            #CF Data
            bins = data['bins'] 
            CF = data['CF']

            #Count rates
            CR = data['countRates']
            countRateCh1 = CR[0]
            countRateCh2 = CR[1]

            #PCHs
            PCH = data['PCH']
            PCH1 = PCH[0]
            PCH2 = PCH[1]

            #Account for single channel collection
            if not np.isnan(PCH2[0][0]):
                    PCH2[0] = np.zeros(len(PCH1[0]))
                    times = PCH1[1][:-1]
            elif not np.isnan(PCH1[0][0]):    
                    PCH1[0] = np.zeros(len(PCH2[0]))
                    times = PCH2[1][:-1]
        
            #Create Data Frames
            df1 = pd.DataFrame({'Bins [us]':bins,'CF':CF})
            df2 = pd.DataFrame({'Ch1 Count Rate (kHz)':[countRateCh1],'Ch2 Count Rate (kHz)':[countRateCh2]})
            df3 = pd.DataFrame({'Times':times,'PCH Ch1':PCH1[0],'PCH Ch2':PCH2[0]})
            
            #Write to Excel
            outFile = NPZfiles[j][:-4]+ '.xls' #Output File Name
            writer = pd.ExcelWriter(outFile)
            df1.to_excel(writer,sheet_name = 'Correlation')
            df2.to_excel(writer,sheet_name = 'Count Rates')
            df3.to_excel(writer,sheet_name = 'PCH')
            writer.save()
            
            
                          

if __name__ == '__main__':
    testFile = [r'C:\Users\mfarrar.MESSIAH\Documents\FCS_Measurements\20181218\NewThorNSLaser_TetraSpeck_1to100_5min_0.95mW_Trial_1Ch1ACF.npz']
    npzToFormat(testFile)
