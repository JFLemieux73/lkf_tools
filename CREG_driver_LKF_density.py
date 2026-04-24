import os,sys
sys.path.append(r'lkf_tools/')
import numpy as np
import pandas as pd
from datetime import timedelta
from lkf_metrics  import *
import pickle
import calendar

#----  CREG_driver_LKF density ------------------------------
#
# Driver that loops through a series of files (dates) and that 
# calls the funtion CREG_lkf_density that calculates the LKF
# density on the CREG domain. 
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
#EXP='run_eg1p0_ef1p5'
#EXP='run_eg1p5_ef1p5'
#EXP='run_eg2p25_ef1p5'
#EXP='run_eg1p16_ef1p75'
#EXP='run_eg1p75_ef1p75'
#EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
EXP='run_eg3p0_ef2p0'
main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag'

FREQ='24H'
SDATE='20050101'
EDATE='20050531'
suffix='_000'
#-----------------------------------------

densitydir=os.path.join(main_dir+'/'+EXP+'/DENSITY/')
fileout='density_lkf_'+SDATE+'_'+EDATE+'.npy'
path_fileout=os.path.join(densitydir+fileout)

if not os.path.isdir(densitydir):
    os.makedirs(densitydir)

if (creggrid == 'creg025'):
    nx=528
    ny=735
elif (creggrid == 'creg12'):
    nx=1580
    ny=2198
else:
    print ("Wrong choice of grid")

density= np.zeros((ny,nx))
tpdensity=np.zeros((ny,nx))

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

n=0
for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    date0ext=date0
    filein='lkf_' + date0ext + '_' + EXP + '_001.npy'
    tpdir=date0ext + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    print(path_filein)
    tpdensity=CREG_lkf_density(date0,creggrid,path_filein)
    n=n+1
    density=np.add(density,tpdensity)
    
deno=n*1.0
density=density/deno

np.save(path_fileout,density,allow_pickle=True)

print('Density analysis done for experiment:')
print(EXP)
