import os,sys
sys.path.append(r'lkf_tools/')
import numpy as np
import pandas as pd
from datetime import timedelta
from lkf_metrics  import *
import pickle
import calendar

#----  CREG_driver_LKF_get_angles ------------------------------
#
# finds pairs of intersecting LKFs, calc angles and identify 
# conjugate fault lines 
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
store_main_dir='/home/jfl001/data/DEVlkfv3/LKF_diag'
SDATE='20050425'
EDATE='20050426'
FREQ='24H'
suffix='0000_iceh_inst'

#-----------------------------------------

store_path=os.path.join(main_dir+'/'+EXP+'/Length')
if not os.path.isdir(store_path):
    os.mkdir(store_path)

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein='lkf_' + date0 + '_' + EXP + '_001.npy'
    tpdir=date0 + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    print(path_filein)
    fileout=os.path.join(store_path + '/' + date0 + '_length_' + EXP + '.py')
    print(fileout)
    lkf_length(date0,creggrid,path_filein,fileout)

print('driver_LKF_length is done')
print(EXP)
