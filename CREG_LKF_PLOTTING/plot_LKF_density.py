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
EXP='run8fb'
main_dir='/home/jfl001/data/Lemieux2022/LKF_diag'
SDATE='20050201'
EDATE='20050228'

#-----------------------------------------

densitydir=os.path.join(main_dir+'/'+creggrid+'/'+EXP+'/DENSITY/')
filein='density_lkf_'+SDATE+'_'+EDATE+'.npy'
path_filein=os.path.join(densitydir+filein)

density = np.load(path_filein,allow_pickle=True)

if creggrid == 'creg025' :
    file1='/fs/homeu2/eccc/mrd/rpnenv/jfl001/Lemieux2022/UTIL/tarea_CREG025ext.nc'
    CDF = CdfFiles(inputfile = file1)
    lat = CDF.GetVar(varname='nav_lat')
    lon = CDF.GetVar(varname='nav_lon')

elif creggrid == 'creg12' :
    file1='/fs/homeu2/eccc/mrd/rpnenv/jfl001/Lemieux2022/UTIL/tmask_area_creg12pe.nc'
    CDF = CdfFiles(inputfile = file1)
    lat = CDF.GetVar(varname='TLAT')
    lon = CDF.GetVar(varname='TLON')

#------ Figure ----------

proj = ccrs.NorthPolarStereo(central_longitude=315)
extent = [180, 0, 60,60]
cmap = 'BuPu'

Figure1 = plt.figure(figsize=[4.0,4.0])

ax =  Figure1.add_axes([0.1, 0.1, 0.8, 0.8],projection=proj)
ax.set_extent(extent)

im = ax.pcolormesh(lon,lat,density,
                           transform=ccrs.PlateCarree(),
                           vmin=0,vmax=0.2,
                           cmap=cmap)

ax.add_feature(cartopy.feature.LAND, zorder=100, edgecolor='k')
Figure1.colorbar(im, orientation='vertical', shrink=0.8)


Figure1.savefig("test.png")
plt.close(Figure1)


