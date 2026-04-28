#load_ext autoreload
#autoreload 2

import numpy as np
import xarray as xr
import os
from pathlib import Path
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

#----- input -----

#ni = 528 ; creg025
#nj = 735 ;

#ni = 1580 ; creg12
#nj = 2198 ;

creggrid='creg12' # creg025 or creg12
EXP='eg1p5_ef1p5'
EXPr='run_eg1.5_ef1.5'
ddate='2005042300'
lkfplot=75
main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag'
main_dirnc='/home/jfl001/data/runsLemieux_et_al_plast_pot/'
delta=5 # subplot has delta cells on four sides around region of interest

#----- define paths and file names --------

filein='lkf_' + ddate + '_' + EXP + '_001.npy'
tpdir=ddate + '_' + EXP
path_filein=os.path.join(main_dir+'/'+EXP+'/'+tpdir+'/'+filein)
data_path=os.path.join(main_dirnc+'/'+EXPr+'/hourly/'+ddate+'0000_iceh_inst.nc')

#----- open npy file -----

lkfs = np.load(path_filein,allow_pickle=True)
print(lkfs.shape)

#----- open nc file and calc tot def -----
# array is opened as j,i in python

creg_nc = xr.open_dataset(data_path)
div = creg_nc.divu[0,:,:]/100.0
shr = creg_nc.shear[0,:,:]/100.0
eps_tot = np.sqrt(div**2+shr**2)

print(eps_tot.shape)

#----- shift indices ---------------------

# arrays (i,j) are read in python as (j,i)

# il y presentement un bug dans les sorties des j,i. 
# les indices ne correspondent pas aux indices de la grille native.
# dans ce code: jl,il indices des LKFs (avec bug) et j,i indices grille native
# jl=lkf[:,0] et il=lkf[:,1].
# Voir courriel de Nils du 4 oct 2022. Pour corriger les i,j je dois faire:
# i = lkf[:,0] + lkf_data.index_x[0][0]
# j = lkf[:,1] + lkf_data.index_y[0][0]

# pour creg025:
# lkf_data.index_x[0][0]=93
# lkf_data.index_y[0][0]=329
# 
# pour creg12:
# lkf_data.index_x[0][0]=278
# lkf_data.index_y[0][0]=985

# je pense que ce que Nils a écrit n'est pas ok. Ça devrait être:

# j = lkf[:,0] + lkf_data.index_y[0][0] - 1
# i = lkf[:,1] + lkf_data.index_x[0][0] - 1

if (creggrid == 'creg025'):
    jshift=329
    ishift=93
elif (creggrid == 'creg12'):
    jshift=985
    ishift=278
else:
    print ("Wrong choice of grid")

#---- analyse chosen lkf -----

l=0
for ilkf in lkfs:
#    print(l)
#    print(ilkf)
    if l == lkfplot:
        nb=ilkf.shape[0] # nb of points in LKF i
        maxjl=np.max(ilkf[:,0])
        minjl=np.min(ilkf[:,0])
        maxil=np.max(ilkf[:,1])
        minil=np.min(ilkf[:,1])

        print(minjl)
        print(maxjl)
        print(minil)
        print(maxil)
#        print(int(maxjl)+jshift)
#        print(int(maxil)+ishift)
        zlkf=ilkf
    l=l+1

print(zlkf)

# define smaller (sub) domain for pcolor plot

jsubfin=int(maxjl-minjl+delta+delta+1)
isubfin=int(maxil-minil+delta+delta+1)
LKFp= np.zeros((jsubfin,isubfin))
eps_totp= np.zeros((jsubfin,isubfin))

# set LKF=1 in sub domain

for n in range(nb):
    jl=zlkf[n,0]
    il=zlkf[n,1]
    jsub=int(jl-minjl+delta)
    isub=int(il-minil+delta)
    LKFp[jsub,isub]=1
#    j=int(jl)+jshift-1
#    i=int(il)+ishift-1
#    print(zlkf[n,4])
#    print(div[j,i])

plt.pcolor(LKFp)
plt.colorbar()
plt.savefig('oneLKF.png')

#---- copy eps_tot in subdomain for pcolor plot ----

for jsub in range(jsubfin):
    for isub in range(isubfin):
        jl=jsub+int(minjl)-delta
        il=isub+int(minil)-delta
        j=jl+jshift-1
        i=il+ishift-1        
        eps_totp[jsub,isub]=eps_tot[j,i]
#        print(eps_totp[jsub,isub])

plt.figure(2)
plt.pcolor(eps_totp, vmin=0.0, vmax=0.2)
plt.colorbar()
plt.savefig('eps_tot.png')

