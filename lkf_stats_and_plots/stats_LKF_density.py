import os,sys
sys.path.append(r'/home/map005/data/eccc-ppp6/gitprojects/SIDD/src/')
import numpy as np
import pandas as pd
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
from datetime import timedelta
import pickle
import calendar
from netCDF4 import Dataset 
from CDFfiles import CdfFiles
import cartopy.crs as ccrs
import cartopy.feature


#----- INPUT -----
#ni = 528 ; creg025
#nj = 735 ;
#ni = 1580 ; creg12
#nj = 2198 ;
creggrid='creg025' # creg025 or creg12
EXP='run7f'
main_dir='/home/jfl001/data/Lemieux2022/LKF_diag'
SDATE='20050201'
EDATE='20050228'
dir_util='/home/jfl001/Lemieux2022/UTIL'
mindist=150 # km
latmin=75 # IMPROVE THIS!!!!

#-----------------------------------------

densitydir=os.path.join(main_dir+'/'+creggrid+'/'+EXP+'/DENSITY/')
filein='density_lkf_'+SDATE+'_'+EDATE+'.npy'
path_filein=os.path.join(densitydir+filein)

density = np.load(path_filein,allow_pickle=True)

if creggrid == 'creg025' :
    file1='/fs/homeu2/eccc/mrd/rpnenv/jfl001/Lemieux2022/UTIL/tarea_CREG025ext.nc'
    CDF = CdfFiles(inputfile = file1)
    area = CDF.GetVar(varname='tarea')
    lat = CDF.GetVar(varname='nav_lat')
    lon = CDF.GetVar(varname='nav_lon')
    nx=528
    ny=735
    masktp = CDF.GetVar(varname='tmask')
    mask= np.zeros((ny,nx))
    mask[:,:]=masktp[0,:,:]

elif creggrid == 'creg12' :
    file1='/fs/homeu2/eccc/mrd/rpnenv/jfl001/Lemieux2022/UTIL/tmask_area_creg12pe.nc'
    CDF = CdfFiles(inputfile = file1)
    lat = CDF.GetVar(varname='TLAT')
    lon = CDF.GetVar(varname='TLON')
    area = CDF.GetVar(varname='tarea')
    nx=1580
    ny=2198
    mask = CDF.GetVar(varname='tmask')

#----- open distance to land file --------

path_filedist=os.path.join(dir_util +'/dist_'+creggrid+'.pkl')
dist = np.load(path_filedist,allow_pickle=True)

#-----------------------------------------

area[:,:]=area[:,:]/1e6 # in km2

mdensity=0.0
totarea=0.0
for j in range(ny):
    for i in range(nx):
        if lat[j,i] > latmin:
            if dist[j,i] > mindist:
#                if mask[j,i] == 1 and dist[j,i] > mindist:
                totarea=totarea+area[j,i]
                mdensity=mdensity + density[j,i]*area[j,i]

mdensity=mdensity/totarea

print("Mean density is:")
print(mdensity)
        

