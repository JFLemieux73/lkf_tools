import os,sys
sys.path.append(r'lkf_tools/')
import numpy as np
import pandas as pd
from datetime import timedelta
from lkf_metrics import lkf_concatenate_width
import pickle
import calendar

#----  driver_concatenate_width ------------------------------
#
# Driver that loops through a series of files (dates) and that 
# calls the funtion lkf_concatenate_width. This function
# concatenates the half widths for one LKF file (one date) and
# the concatenation for multiple files (mutiple dates) is done
# here in the driver.
#
#------------------------------------------------------------

#----- INPUT -----
EXP='run_eg1p75_ef1p75'
main_dir='/home/jfl001/data/DEVlkfv3/LKF_diag'

FREQ='24H'
SDATE='20050425'
EDATE='20050426'
suffix='_000'
fraclabel='0p5'
dsearch=5 # +- dsearch cells around one LKF cell (dist is capped if searching too far!!!)
#-----------------------------------------

dsstr=str(dsearch)

widthdir=os.path.join(main_dir+'/'+EXP+'/WIDTH/')

if not os.path.isdir(widthdir):
    os.makedirs(widthdir)

fileout1='hwidth1_lkf_'+SDATE+'_'+EDATE+'_f'+fraclabel+'_ds'+dsstr+'.npy'
path_fileout1=os.path.join(widthdir+fileout1)
fileout2='hwidth2_lkf_'+SDATE+'_'+EDATE+'_f'+fraclabel+'_ds'+dsstr+'.npy'
path_fileout2=os.path.join(widthdir+fileout2)

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

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
