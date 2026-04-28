import os,sys
import numpy as np
import pandas as pd
#import matplotlib as plt
import matplotlib.pyplot as plt
from datetime import timedelta
#import pickle
import calendar

#EXP1='run_eg1p75_ef1p5'
#label1='e_f=1.5, e_g=1.75'
EXP1='run_eg1p16_ef1p75'
label1='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=1.16'
EXP2='run_eg1p75_ef1p75'
label2='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=1.75'
EXP3='run_eg2p63_ef1p75'
label3='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=2.63'
#EXP3='run_eg1p75_ef2p0'
#label3='e_f=2.0, e_g=1.75'


main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag_pack/'
zdir='Length'
year='2005'
SDATE=year+'0101'
EDATE=year+'0531'
FREQ='24H'
addlabel='length'

#-----------------------------------------

list_dates=list(pd.date_range(SDATE,EDATE, freq=FREQ))

mlength1=[] # mean length
tlength1=[] # total length
mlength2=[] # mean length
tlength2=[] # total length
mlength3=[] # mean length
tlength3=[] # total length
datesl=[] # lits of dates
for i in range(len(list_dates)) :
    date0 = (list_dates[i] + timedelta(days=-0)).strftime('%Y%m%d%H')
    filein1=date0+'_'+addlabel+'_'+EXP1+'.py'
    path_filein1=os.path.join(main_dir+'/'+EXP1+'/'+zdir+'/'+filein1)
    df1 = pd.read_csv(path_filein1)
    mlength1.append(df1['length'].mean())
    tlength1.append(df1['length'].sum())
    datesl.append(list_dates[i])

    filein2=date0+'_'+addlabel+'_'+EXP2+'.py'
    path_filein2=os.path.join(main_dir+'/'+EXP2+'/'+zdir+'/'+filein2)
    df2 = pd.read_csv(path_filein2)
    mlength2.append(df2['length'].mean())
    tlength2.append(df2['length'].sum())

    filein3=date0+'_'+addlabel+'_'+EXP3+'.py'
    path_filein3=os.path.join(main_dir+'/'+EXP3+'/'+zdir+'/'+filein3)
    df3 = pd.read_csv(path_filein3)
    mlength3.append(df3['length'].mean())
    tlength3.append(df3['length'].sum())

#--- calc mean values for the whole time series

print('mean of mean length')
print(np.mean(mlength1),np.mean(mlength2),np.mean(mlength3))
print('mean of total length')
print(np.mean(tlength1),np.mean(tlength2),np.mean(tlength3))

#--- create the panda dataframes for plotting

dfpm = pd.DataFrame(datesl, columns=['date'])
dfpm.insert(1, 'mean_length1', mlength1)
dfpm.insert(2, 'mean_length2', mlength2)
dfpm.insert(3, 'mean_length3', mlength3)

dfpt = pd.DataFrame(datesl, columns=['date'])
dfpt.insert(1, 'total_length1', tlength1)
dfpt.insert(2, 'total_length2', tlength2)
dfpt.insert(3, 'total_length3', tlength3)


ax = dfpm.plot(x = 'date', y =['mean_length1', 'mean_length2', 'mean_length3'], color =['dodgerblue', 'orange', 'darkviolet'])
ax.legend([label1, label2, label3],loc='lower right')
ax.set_xlabel("", fontsize='2')
ax.set_ylabel("Mean length of LKFs (km)", fontsize=14)
ax.set_ylim(0, 400) 
fileout='FIGS/Mean_length_LKFs_ef1p75_'+year+'.png'
#fileout='FIGS/Mean_length_LKFs_eg1p75_'+year+'.png'
plt.savefig(fileout)

ax = dfpt.plot(x = 'date', y =['total_length1', 'total_length2', 'total_length3'], color =['dodgerblue', 'orange', 'darkviolet'])
ax.legend([label1, label2, label3],loc='upper right')
ax.set_xlabel("", fontsize='2')
ax.set_ylabel("Total length of LKFs (km)", fontsize=14)
ax.set_ylim(0, 60000)
fileout='FIGS/Total_length_LKFs_ef1p75_'+year+'.png'
#fileout='FIGS/Total_length_LKFs_eg1p75_'+year+'.png'
plt.savefig(fileout)

plt.show()
