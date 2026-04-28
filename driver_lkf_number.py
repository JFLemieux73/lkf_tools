import os,sys
sys.path.append(r'lkf_tools/')
import numpy as np
import pandas as pd
from datetime import timedelta
import pickle
import calendar

#----  driver_lkf_number ------------------------------------
#
# Driver that loops through a series of files (dates) and that 
# get the nb of LKFs and store it in output file 
# 
# note: there is no condition applied here for distance to 
#       land. This could be applied later for plotting. 
#
#------------------------------------------------------------

#----- INPUT -----
#ni = 528 ; creg025
#nj = 735 ;
#ni = 1580 ; creg12
#nj = 2198 ;
creggrid='creg12' # creg025 or creg12
EXP='run_eg1p75_ef1p75'

main_dir='/home/jfl001/data/DEVlkfv3/LKF_diag'

SDATE='20050425'
EDATE='20050426'
FREQ='24H'

#-----------------------------------------

nbLKFdir=os.path.join(main_dir+'/'+EXP+'/nbLKFs/')
fileout='number_lkf_'+SDATE+'_'+EDATE+'.npy'
path_fileout=os.path.join(nbLKFdir+fileout)

if not os.path.isdir(nbLKFdir):
    os.makedirs(nbLKFdir)

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

nbvec=[]
datevec=[]
for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein='lkf_' + date0 + '_' + EXP + '_001.npy'
    tpdir=date0 + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    print(path_filein)
    lkfs = np.load(path_filein,allow_pickle=True)
    tpnb=lkfs.shape[0]
    nbvec.append(tpnb)
    datevec.append(list_dates[i])

# Create the pandas DataFrame
df = pd.DataFrame(datevec, columns=['date'])
df.insert(1, 'nb_of_LKFS', nbvec)
print(df)

df.to_csv(path_fileout, index=False)

print('Analysis of LKF number done for experiment:')
print(EXP)
