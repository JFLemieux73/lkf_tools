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
vortflag=2 # 1: output includes vorticity, 2: no vorticity
creggrid='creg12' # creg025 or creg12
#EXP='control'
#main_dir='/home/chh005/data/ppp6/maestro_archives/IC4/RXFC24LONG19V1/SAM2'
EXP='exp1'
main_dir='/home/phb001/data/ppp6/maestro_archives/riops-a/rx-multicat-leads-1/SAM2'
main_dir_grid='/home/socn000/data/eccc-ppp5/env_rhel-8-icelake-64/datafiles/constants/oce/repository/master/CONCEPTS/'
store_main_dir='/home/jfl001/data/LKF_rips_analysis'
kvalue=7 # value for kernel
produce_plot=True
SDATEa='20200930' # start date analysis...history file start 7 days before
EDATEa='20200930' # end   date analysis...history file start 7 days before
FREQ='168H'
suffix='_003_iau' # IMPORTANT...verify a specific hour

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

list_dates=list(pd.date_range(SDATEa,EDATEa, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-7)).strftime('%Y%m%d%H')
    datea = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d')
    dir_anal=os.path.join(main_dir+'/'+datea)
    data_path=os.path.join(dir_anal+'/CICE/history/'+date0+suffix+'.nc')
    fileout=date0 + suffix + '_' + EXP
    print(fileout)
    lkf_detect(date0, creggrid, vortflag, grid_path, data_path, store_path, fileout, kvalue, produce_plot)

print('Detection done for experiment:')
print(EXP)
