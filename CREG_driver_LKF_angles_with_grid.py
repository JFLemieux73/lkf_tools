import os,sys
import numpy as np
import pandas as pd
from datetime import timedelta
from CREG_lkf_tools  import *
import pickle
import calendar

#----  CREG_driver_LKF_angles_with_grid ---------------------
#
# finds minimum angle of LKF (at mid-point) with x or y axis
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

# Important: given midpoint mp with coordinates (imp,jmp), polyfit on LKF is done for the region:
# mp-delta to mp + delta. 

creggrid='creg12' # creg025 or creg12
EXP='run_eg1p5_ef1p5'
main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag'
SDATE='20050101'
EDATE='20050101'
FREQ='24H'
suffix='0000_iceh_inst'
delta=5 

#-----------------------------------------

dlabel=str(delta)

store_path=os.path.join(main_dir+'/'+EXP+'/Angle_grid')
if not os.path.isdir(store_path):
    os.mkdir(store_path)

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein='lkf_' + date0 + '_' + EXP + '_001.npy'
    tpdir=date0 + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    print(path_filein)
    fileout=os.path.join(store_path + '/' + date0 + '_anggrid_' + EXP + '_delta' + dlabel +'.py')
    print(fileout)
    CREG_lkf_angles_with_grid(date0,creggrid,path_filein,fileout,delta)

print('CREG_driver_LKF_angles_with_grid is done')
print(EXP)
