import os,sys
sys.path.append(r'lkf_tools/')
import numpy as np
import pandas as pd
from datetime import timedelta
from lkf_metrics  import lkf_calc_width,lkf_concatenate_width
import pickle
import calendar

#----  driver_lkf_calc_width ---------------------------------
#
# Driver that loops through a series of files (dates) and that 
# calls the funtion lkf_calc_width that calculates the LKF
# half widths. It then concatenates the width data for analysis.
#
#-------------------------------------------------------------

#----- INPUT -----
grid='creg12' # creg025 or creg12
#ni = 528 ; creg025
#nj = 735 ;
#ni = 1580 ; creg12
#nj = 2198 ;

EXP='run_eg1p75_ef1p75'
main_dir='/home/jfl001/data/LKF_diag'
main_dirnc='/home/jfl001/data/Model_outputs'
#dir_util='/home/jfl001/data/Lemieux2022/UTIL'
dsearch=5 # +- dsearch cells around one LKF cell (dist is capped if searching too far!!!)
frac=0.5 # half width is defined as eps_tot < frac*LKFepsmax 
#mindist=0.0 # LKF point is analysed if dist from land > mindist (km)
FREQ='24H'
SDATE='20050101'
EDATE='20050102'
suffix='0000_iceh_inst'

#------------------------------------------------------------

if (grid == 'creg025'):
    jshift=329
    ishift=93
elif (grid == 'creg12'):
    jshift=985
    ishift=278
else:
    print ("Wrong choice of grid")

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

dsstr=str(dsearch)

#---- calc width --------------------------------------------------

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    date0ext=date0
    filein='lkf_' + date0ext + '_' + EXP + '_001.npy'
    fileout='lkf_' + date0ext + '_' + EXP + '_f' + fraclabel +'_ds'+dsstr+'.npy'
    tpdir=date0ext + '_' + EXP
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    path_fileout=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+fileout)
    data_pathnc=os.path.join(main_dirnc+'/'+EXP+'/hourly/'+date0+suffix+'.nc')
    #path_filedist=os.path.join(dir_util +'/dist_'+creggrid+'.pkl')

    lkf_calc_width(date0,path_filein,path_fileout,data_pathnc,dsearch,frac,ishift,jshift)
    #lkf_calc_width(date0,creggrid,path_filedist,path_filein,path_fileout,data_pathnc,dsearch,frac,mindist)

print('Width analysis done for experiment:')
print(EXP)


#---- concatenate width data for analysis ------------------------

widthdir=os.path.join(main_dir+'/'+EXP+'/WIDTH/')

if not os.path.isdir(widthdir):
    os.makedirs(widthdir)

fileout1='hwidth1_lkf_'+SDATE+'_'+EDATE+'_f'+fraclabel+'_ds'+dsstr+'.npy'
path_fileout1=os.path.join(widthdir+fileout1)
fileout2='hwidth2_lkf_'+SDATE+'_'+EDATE+'_f'+fraclabel+'_ds'+dsstr+'.npy'
path_fileout2=os.path.join(widthdir+fileout2)

hwidth1=[]
hwidth2=[]
tpvect=[]
for i in range(len(list_dates)):
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    date0ext=date0
    filein='lkf_'+date0ext+'_'+EXP+'_f'+fraclabel+'_ds'+dsstr+'.npy'
    tpdir=date0ext+'_'+EXP
    
    tpvect=[]
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    tpvect=lkf_concatenate_width (date0, path_filein, hwidth=1)
    hwidth1.extend(tpvect)

    tpvect=[]
    path_filein=os.path.join(main_dir+'/'+EXP+'/detectedLKFs/'+tpdir+'/'+filein)
    tpvect=lkf_concatenate_width (date0, path_filein, hwidth=2)
    hwidth2.extend(tpvect)

np.save(path_fileout1,hwidth1,allow_pickle=True)
np.save(path_fileout2,hwidth2,allow_pickle=True)

print('Concatenation done for experiment:')
print(EXP)
