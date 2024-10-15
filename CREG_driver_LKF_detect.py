import os,sys
import numpy as np
import pandas as pd
from datetime import timedelta
from CREG_lkf_tools  import *
import pickle
import calendar

#----  CREG_driver_LKF_detect -------------------------------
#
# Driver that loops through a series of files (dates) and that 
# calls the funtion CREG_lkf_detect.
#
#------------------------------------------------------------

#----- INPUT -----
#ni = 528 ; creg025
#nj = 735 ;
#ni = 1580 ; creg12
#nj = 2198 ;
cregflag=1 # 1: output includes vorticity, 2: no vorticity
creggrid='creg12' # creg025 or creg12

#EXP='run_eg1p0_ef1p5'
#EXP='run_eg1p5_ef1p5'
#EXP='run_eg2p25_ef1p5'
#EXP='run_eg1p16_ef1p75'
EXP='run_eg1p75_ef1p75'
#EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
#EXP='run_eg3p0_ef2p0'

main_dir='/home/jfl001/data/runsLemieux_et_al_plast_pot/'
main_dir_grid='/home/socn000/data/eccc-ppp5/env_rhel-8-icelake-64/datafiles/constants/oce/repository/master/CONCEPTS/'
store_main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag_pack'
kvalue=7 # value for kernel
produce_plot=False
SDATE='20050101'
EDATE='20050531'
FREQ='24H'
suffix='0000_iceh_inst'

#----- check kernel value ----------------
# kvalue should be odd: see Nils' email (4 nov 2022)

if kvalue % 2 == 0:
    print("kernel value should be an odd integer") 
    exit()
else:
    print("kernel value = ") 
    print(kvalue)

#----- define paths and file name --------

if (creggrid == 'creg025'):
    grid_path=os.path.join(main_dir_grid+'/creg025pe/grid/coordinates_CREG025_LIM.nc')
elif (creggrid == 'creg12'):
    grid_path=os.path.join(main_dir_grid+'/creg012pe/grid/coordinates_CREG12_ext.nc')
else:
    print ("Wrong choice of grid")

store_path=os.path.join(store_main_dir+'/'+EXP+'/detectedLKFs/')

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    data_path=os.path.join(main_dir+'/'+EXP+'/hourly/'+date0+suffix+'.nc')
    fileout=date0 + '_' + EXP
    print(fileout)
    CREG_lkf_detect(date0, creggrid, cregflag, grid_path, data_path, store_path, fileout, kvalue, produce_plot)

print('Detection done for experiment:')
print(EXP)
