import os,sys
import numpy as np
import pandas as pd
from datetime import timedelta
from CREG_lkf_tools  import *
import pickle
import calendar

#----  CREG_driver_LKF_calc_width ---------------------------
#
# Driver that loops through a series of files (dates) and that 
# calls the funtion CREG_lkf_calc_width that calculates the LKF
# half widths.
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
EXP='run_eg1p75_ef1p75'
#EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
#EXP='run_eg3p0_ef2p0'

#EXP='run_eg1p75_ef1p16'
#EXP='run_eg1p75_ef1p5'
#EXP='run_eg1p75_ef2p0'
#EXP='run_eg1p75_ef2p63'

main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag_pack'
main_dirnc='/home/jfl001/data/runsLemieux_et_al_plast_pot/'
dir_util='/home/jfl001/Lemieux2022/UTIL'
dsearch=5 # +- dsearch cells around one LKF cell (dist is capped if searching too far!!!)
frac=0.5 # half width is defined as eps_tot < frac*LKFepsmax 
mindist=0.0 # LKF point is analysed if dist from land > mindist (km)

FREQ='24H'
SDATE='20050101'
EDATE='20050102'
suffix='0000_iceh_inst'

#----- label for width criterion ---------------------------

if frac == 0.25:
    fraclabel='0p25'
elif frac == 0.5:
    fraclabel='0p5'
elif frac == 0.75:
    fraclabel='0p75'
else:
    print('frac value is not allowed')
    exit()

#-----------------------------------------------------------

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    date0ext=date0
    filein='lkf_' + date0ext + '_' + EXP + '_001.npy'
    fileout='lkf_' + date0ext + '_' + EXP + '_' + fraclabel +'.npy'
    tpdir=date0ext + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    path_fileout=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+fileout)
    #data_path=os.path.join(main_dirnc+'/'+EXP+'/hourly/'+date0ext+'.nc')
    data_pathnc=os.path.join(main_dirnc+'/'+EXP+'/hourly/'+date0+suffix+'.nc')
    path_filedist=os.path.join(dir_util +'/dist_'+creggrid+'.pkl')

    CREG_lkf_calc_width(date0,creggrid,path_filedist,path_filein,path_fileout,data_pathnc,dsearch,frac,mindist)

print('Width analysis done for experiment:')
print(EXP)
