import os,sys
import numpy as np
import pandas as pd
from datetime import timedelta
from CREG_lkf_tools  import *
import pickle
import calendar

#----  driver_LKF_detect ----------------------------------------
#
# Driver that loops through a series of netcdf files (dates) and 
# that calls the funtion lkf_detect.
#
# The detection algo was tested for the CONCEPTS regional (creg)
# grids. The code aborts for other grids. Using another grid 
# would need careful testing for a proper detection of LKFs. 
#
# The coordinate file for the grid should include lat,lon and 
# the x and y dimensions of the cells.
#
#----------------------------------------------------------------

#----- INPUT -----
#ni = 528 ; creg025
#nj = 735 ;
#ni = 1580 ; creg12
#nj = 2198 ;
vortflag=1 # 1: output includes vorticity, 2: no vorticity
grid='creg12' # creg025 or creg12

#EXP='run_eg1p0_ef1p5'
#EXP='run_eg1p5_ef1p5'
#EXP='run_eg2p25_ef1p5'
#EXP='run_eg1p16_ef1p75'
EXP='run_eg1p75_ef1p75'
#EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
#EXP='run_eg3p0_ef2p0'

main_dir='/home/jfl001/data/TESTlkf'
main_dir_grid='/home/socn000/data/ppp8/env_rhel-9-graniterapids-64/datafiles/constants/oce/repository/master/CONCEPTS/'
store_main_dirTP='/home/jfl001/data/DEVlkfv3'
kvalue=7 # value for kernel
produce_plot=True
pack_ice_mask=False
SDATE='20050425'
EDATE='20050425'
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

if (grid == 'creg025'):
    grid_path=os.path.join(main_dir_grid+'/creg025pe/grid/coordinates_CREG025_LIM.nc')
elif (grid == 'creg12'):
    grid_path=os.path.join(main_dir_grid+'/creg012pe/grid/coordinates_CREG12_ext.nc')
else:
    print ("Wrong choice of grid")

if (pack_ice_mask):
    store_main_dir=store_main_dirTP+'/LKF_diag_pack'
else:
    store_main_dir=store_main_dirTP+'/LKF_diag'

store_path=os.path.join(store_main_dir+'/'+EXP+'/detectedLKFs/')

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    data_path=os.path.join(main_dir+'/'+EXP+'/hourly/'+date0+suffix+'.nc')
    fileout=date0 + '_' + EXP
    print(fileout)
    lkf_detect(date0, grid, vortflag, grid_path, data_path, store_path, fileout, kvalue, produce_plot, pack_ice_mask)

print('Detection done for experiment:')
print(EXP)
