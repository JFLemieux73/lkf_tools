#load_ext autoreload
#autoreload 2

import numpy as np
#import xarray as xr
import os
from pathlib import Path
import matplotlib.pyplot as plt
#import cartopy.crs as ccrs

creggrid='creg025' # creg025 or creg12
EXP='run9f'
SDATE='20050201'
EDATE='20050228'
main_dir='/home/jfl001/data/Lemieux2022/LKF_diag'
fig_dir='/home/jfl001/data/Lemieux2022/LKF_diag/Histo_width'
#mybins=np.linspace(0, 15, 101)

nbbins=71
delta=0.2
mybins=np.zeros(nbbins+1)
binc=np.zeros(nbbins)
for b in range(nbbins+1):
    mybins[b]=0.9+b*delta

for b in range(nbbins):
    binc[b]=0.5*(mybins[b]+mybins[b+1])

print(mybins)
print(binc)

#----- define paths and file names --------

filein1='hwidth1_lkf_'+SDATE+'_'+EDATE+'.npy'
path_filein1=os.path.join(main_dir+'/'+creggrid+'/'+EXP+'/WIDTH/'+filein1)
filein2='hwidth2_lkf_'+SDATE+'_'+EDATE+'.npy'
path_filein2=os.path.join(main_dir+'/'+creggrid+'/'+EXP+'/WIDTH/'+filein2)
fileout='histo_width_lkf_'+SDATE+'_'+EDATE+'_'+EXP+'.png'
path_fileout=os.path.join(fig_dir+'/'+fileout)

#----- open npy files -----

hwidth1 = np.load(path_filein1,allow_pickle=True)
hwidth2 = np.load(path_filein2,allow_pickle=True)

npoints=hwidth1.shape[0]
width=np.zeros(npoints)
width[:]=hwidth1[:]+hwidth2[:]
print('number of LKF points:')
print(npoints)
print('mean values for hw1, hw2 and width are:')
print(np.mean(hwidth1))
print(np.mean(hwidth2))
print(np.mean(width))

counts, bins, bars = plt.hist(width, bins=mybins, color = "dodgerblue", ec="dodgerblue")#, norm_hist=True)
#plt.hist(hwidth2, bins=mybins, alpha=0.3, color = "magenta", ec="magenta")
#plt.hist(Ddef2, bins=mybins, alpha=0.3, color = "orange", ec="orange", )
#plt.yscale('log')
#plt.xlabel('LKF width', fontsize=14)
#plt.ylabel('Fraction of counts', fontsize=14)
#plt.legend([label1, label2], loc ="upper right", markerscale=1)
counts = counts / npoints
#plt.bar(courses, values, color ='maroon', width = 0.4)

print('Sum should be = 1.0')
print(np.sum(counts))

plt.figure(2)
plt.bar(binc,counts, width = 0.2)
plt.xlabel('LKF width', fontsize=14)
plt.ylabel('Fraction of counts', fontsize=14)
plt.xlim([0, 15]) 
plt.ylim([0, 0.45]) 
plt.savefig(path_fileout)
#plt.savefig('youhhh.png')


