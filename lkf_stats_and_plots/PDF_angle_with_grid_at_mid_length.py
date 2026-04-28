import os,sys
import numpy as np
import pandas as pd
#import matplotlib as plt
import matplotlib.pyplot as plt
from datetime import timedelta
#import pickle
import calendar

#EXP='run_eg1p0_ef1p5'
#EXP='run_eg1p5_ef1p5'
#EXP='run_eg2p25_ef1p5'
#EXP='run_eg1p16_ef1p75'
#EXP='run_eg1p75_ef1p75'
EXP='run_eg2p63_ef1p75'
#EXP='run_eg1p33_ef2p0'
#EXP='run_eg2p0_ef2p0'
#EXP='run_eg3p0_ef2p0'
year='2005'
main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag'
zdir='Angle_grid_at_mid_length'
SDATE=year+'0101'
EDATE=year+'0531'
FREQ='24H'
addlabel='anggrid_ml'
dlabel='10'

#-----------------------------------------

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein=date0+'_'+addlabel+EXP+ '_delta' + dlabel +'.py'
    path_filein=os.path.join(main_dir+'/'+EXP+'/'+zdir+'/'+filein)
    if i==0: # date0 is SDATE
        df1 = pd.read_csv(path_filein)
    else:
        df2 = pd.read_csv(path_filein)
        df1 = pd.concat([df1, df2])

#--- define bins 0-90 deg ---
nbbins=36 #2.5*36=90
delta=2.5
mybins=np.zeros(nbbins+1)
binc=np.zeros(nbbins)
for b in range(nbbins+1):
    mybins[b]=b*delta

for b in range(nbbins):
    binc[b]=0.5*(mybins[b]+mybins[b+1])

#--- define bins 0-45 deg ---
nbbins=18 #2.5*18=45
delta=2.5
myotherbins=np.zeros(nbbins+1)
otherbinc=np.zeros(nbbins)
for b in range(nbbins+1):
    myotherbins[b]=b*delta

for b in range(nbbins):
    otherbinc[b]=0.5*(mybins[b]+mybins[b+1])

#--- calc mean values ---
mean_x_angle=df1['x_angle'].mean()
print('mean angle with x axis', mean_x_angle)
mean_y_angle=df1['y_angle'].mean()
print('mean angle with y axis', mean_y_angle)
mean_min_angle=df1['min_angle'].mean()
print('mean min angle with x or y axis', mean_min_angle)

plt.figure(1)
counts, bins, bars = plt.hist(df1['x_angle'], bins=mybins, density=True, color = "dodgerblue", ec="dodgerblue")
plt.xlabel('angle', fontsize=14)
plt.ylabel('PDF (angle with x axis)', fontsize=14)
plt.figure(2)
counts, bins, bars = plt.hist(df1['y_angle'], bins=mybins, density=True, color = "dodgerblue", ec="dodgerblue")
plt.xlabel('angle', fontsize=14)
plt.ylabel('PDF (angle with y axis)', fontsize=14)
plt.figure(3)
counts, bins, bars = plt.hist(df1['min_angle'], bins=myotherbins, density=True, color = "dodgerblue", ec="dodgerblue")
plt.xlabel('Minimum angle with x or y axis', fontsize=14)
plt.ylabel('PDF', fontsize=14)
plt.ylim(0,0.08)
plt.xlim(0,45)
fileout='FIGS/PDF_min_angle_grid_at_mid_length_'+EXP+'_delta' + dlabel +'.png'
plt.savefig(fileout)

plt.show()
