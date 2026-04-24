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

# Important: given intersection point ip with coordinates (ip,jp), polyfit on LKF is done for the region ip-delta to ip + delta. 

creggrid='creg12' # creg025 or creg12

#EXP='run_eg1p0_ef1p5'
EXP='run_eg1p5_ef1p5'
#EXP='run_eg2p25_ef1p5'
#EXP='run_eg1p16_ef1p75'
#EXP='run_eg1p75_ef1p75'
#EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
#EXP='run_eg3p0_ef2p0'

main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag'
main_dirnc='/home/jfl001/data/runsLemieux_et_al_plast_pot'
SDATE='20050101'
EDATE='20050531'
FREQ='24H'
suffix='0000_iceh_inst'
delta=10

#-----------------------------------------

dlabel=str(delta)

store_path1=os.path.join(main_dir+'/'+EXP+'/Int_Angle')
if not os.path.isdir(store_path1):
    os.mkdir(store_path1)

store_path2=os.path.join(main_dir+'/'+EXP+'/Angle_grid_at_int')
if not os.path.isdir(store_path2):
    os.mkdir(store_path2)

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein='lkf_' + date0 + '_' + EXP + '_001.npy'
    tpdir=date0 + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    data_pathnc=os.path.join(main_dirnc+'/'+EXP+'/hourly/'+date0+suffix+'.nc')
    print(path_filein)
    print(data_pathnc)
    fileout1=os.path.join(store_path1 + '/' + date0 + '_intpairs_' + EXP + '_delta' + dlabel +'.py')
    fileout2=os.path.join(store_path2 + '/' + date0 + '_anggrid_at_int_' + EXP + '_delta' + dlabel +'.py')
    print(fileout1)
    CREG_lkf_pairs_and_angles(date0,creggrid,path_filein,data_pathnc,fileout1,fileout2,delta)

print('CREG_driver_LKF_pairs_and_angles is done')
print(EXP)
