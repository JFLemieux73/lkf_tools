import numpy as np
import math
import xarray as xr
import pandas as pd
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from pathlib import Path
#from scipy.optimize import fsolve
from shapely.geometry import LineString
from lkf_tools.dataset import *

#----  lkf_detect -------------------------------------------
#
# Prepares netcdf outputs to be used by Nils' LKF
# detection algorithm. Also offers possibility to plot 
# detected LKFs on pan-Arctic grid (produce_plot=True).
#
#------------------------------------------------------------

def lkf_detect(date, creggrid, vortflag, grid_path, data_path, store_path, fileout, kvalue, produce_plot, pack_ice_mask):

    print(fileout)

#----- open netcdf file -----

    creg_nc = xr.open_dataset(data_path)

    if vortflag == 1:
        variables = ['divu','shear','vort','aice','uvel','vvel']
        creg_nc = xr.open_dataset(data_path)
        creg_nc=creg_nc[variables]
        creg_nc = creg_nc.rename({'nj':'y','ni':'x','divu':'div', 'shear':'shr', 'vort':'vor', 'aice':'A', 
                                  'uvel':'U', 'vvel':'V'})
    elif vortflag == 2:
        variables = ['divu','shear','aice','uvel','vvel']
        creg_nc = xr.open_dataset(data_path)
        creg_nc=creg_nc[variables]
        creg_nc = creg_nc.rename({'nj':'y','ni':'x','divu':'div', 'shear':'shr', 'aice':'A', 
                                  'uvel':'U', 'vvel':'V'})

#----- open grid coordinate file -----

# WATCHOUT: in the code here U,V,A, shr,div and vor are collocated. 
#           All are ok for my creg12 runs except uvel and vvel (U point) but they
#           are not needed for detect. I would have to check this if I use lkf_tracking
#           ULAT and ULON here are in fact at the T point. This is why I use nav_lat and 
#           nav_lon to define these. 
#
#           For some reasons .rename does not allow ULON and ULAT...it says there is a conflict.
#           ULONtp and ULATtp work fine. I had to make small modifs to dataset.py

    variables = ['e1t', 'e2t', 'nav_lon', 'nav_lat']
    grid_nc = xr.open_dataset(grid_path)
    grid_nc = grid_nc[variables]
    grid_nc = grid_nc.rename({'e1t':'DXU', 'e2t':'DYV', 'nav_lat':'ULATtp', 'nav_lon':'ULONtp'})

    creg_nc = xr.Dataset.merge(creg_nc, grid_nc,compat='override')

#creg_nc = creg_nc.rename({'ni':'x', 'nj':'y','divu':'div', 'shear':'shr', 'aice':'A', 
#                          'uvel':'U', 'vvel':'V', 'TLON':'ULON', 'TLAT':'ULAT'})

#---- process data and detect LKFs ---

# il y presentement un bug dans les sorties des i,j. i est lkf[:,0] et j lkf[:,1].
# Voir courriel de Nils du 4 oct 2022. Pour corriger les i,j je dois faire:
# i = lkf[:,0] + lkf_data.index_x[0][0]
# j = lkf[:,1] + lkf_data.index_y[0][0]
#
# pour creg025:
# lkf_data.index_x[0][0]=93
# lkf_data.index_y[0][0]=329
# 
# pour creg12:
# lkf_data.index_x[0][0]=278
# lkf_data.index_y[0][0]=985

    print('call process_dataset')

    lkf_data = process_dataset(fileout,creg=vortflag, usepmask=pack_ice_mask, output_path=store_path,
                               xarray=creg_nc, skeleton_kernel=kvalue, t_red=1)

    lkf_data.detect_lkfs(indexes=[0])

#---- plot LKFs ---------------------

    if (produce_plot):
        
        fig = plt.figure(figsize=[10, 5])

        ax = plt.subplot(1, 1, 1, projection=ccrs.Orthographic(0, 90))

        ax.coastlines(zorder=3)

        pcm = ax.pcolormesh(lkf_data.lon[max([0,lkf_data.index_y[0][0]-1]):lkf_data.index_y[0][-1]+2:lkf_data.red_fac,
                                         max([0,lkf_data.index_x[0][0]-1]):lkf_data.index_x[0][-1]+2:lkf_data.red_fac],
                            lkf_data.lat[max([0,lkf_data.index_y[0][0]-1]):lkf_data.index_y[0][-1]+2:lkf_data.red_fac,
                                         max([0,lkf_data.index_x[0][0]-1]):lkf_data.index_x[0][-1]+2:lkf_data.red_fac],
                            np.sum(lkf_data.eps_tot_list,axis=0),transform=ccrs.PlateCarree(),vmin=0,vmax=1e-1,cmap='Greys_r')

        it = lkf_data.indexes[-1]

        lkfs = np.load(lkf_data.lkfpath.joinpath('lkf_%s_%03i.npy' %(lkf_data.netcdf_file.split('/')[-1].split('.')[0],(it+1))),allow_pickle=True)

        i=0
        for ilkf in lkfs:
            if i == 60:
                print(ilkf.shape)

            i=i+1
            if np.min(ilkf[:,2])<-150 and np.max(ilkf[:,2]>150):
                ilkf[ilkf[:,2]<0,2]+=360
            ax.plot(ilkf[:,2],ilkf[:,3],transform=ccrs.PlateCarree())

        print('saving image')
        filefig='mapLKF_'+creggrid+'_'+date+'.png'
        plt.colorbar(pcm,label='total deformation')
        plt.savefig(filefig)

#----  lkf_calc_width ---------------------------------------
#
# Analyses detected LKFs in order to calculate half widths
# of LKFs. Detected LKF points have maximum values of eps_tot. 
# Given a certain direction of an LKF, the half widths are 
# then calculated in perpendicular directions referred to as 
# search directions. The search is done for a max number of 
# cells (dsearch) in a given direction. The half widths are 
# obtained when eps_tot < frac * (eps_tot_max). Half widths 
# are only calculated when the distance of a LKF point 
# (grid cell) from land is larger than mindist.
#
#------------------------------------------------------------

def lkf_calc_width(date,creggrid,path_filedist,path_filein,path_fileout,data_path,dsearch,frac,mindist):
    
    print('working on date:')
    print(date)

#----- open npy file -----

    lkfs = np.load(path_filein,allow_pickle=True)
    print(lkfs.shape)

#----- open nc file and calc tot def -----
# array is opened as j,i in python

    creg_nc = xr.open_dataset(data_path)
    div = creg_nc.divu[0,:,:]/100.0
    shr = creg_nc.shear[0,:,:]/100.0
    eps_tot = np.sqrt(div**2+shr**2)

#----- open distance to land file --------

    dist = np.load(path_filedist,allow_pickle=True)

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

#---- analyse  lkfs -----

    out_lkfs=[]
    l=0
    for ilkf in lkfs:
        nb=ilkf.shape[0] # nb of points in LKF i
        maxjl=np.max(ilkf[:,0])
        minjl=np.min(ilkf[:,0])
        maxil=np.max(ilkf[:,1])
        minil=np.min(ilkf[:,1])
        
        zlkf=ilkf

#---- find search direction and width (MV to function...)--------------------
#  
# The search direction is found by defining 3 vectors (v,v1 and v2). 
# v is in the diection of the LKF from n=0...n=nb. v1 and v2 indicate the 
# search direction (there is 180 deg between v1 and v2). v1 is obtained by a 
# 'regle de la main droite'. The index (nail up) points in the direction of v 
# and the thumb indicates the direction of v1. 
# jl = zlkf[:,0], il=zlkf[:,1]
#----------------------------------------------------------------------------

        halfw1=np.zeros(nb)
        halfw2=np.zeros(nb)
 
        for n in range(nb):

            jl = int(zlkf[n,0])
            il = int(zlkf[n,1])
            j=jl+jshift-1
            i=il+ishift-1 

            if (n == 0):
                deltj=zlkf[1,0]-zlkf[0,0]
                delti=zlkf[1,1]-zlkf[0,1]
            elif (n == nb-1):
                deltj=zlkf[n,0]-zlkf[n-1,0]
                delti=zlkf[n,1]-zlkf[n-1,1]
            else:
                deltj=zlkf[n+1,0]-zlkf[n-1,0]
                delti=zlkf[n+1,1]-zlkf[n-1,1]
        
# v vector is written as av,bv = av x^ + bv y^ (x^,y^=unit vectors along i and j)
# v, v1 and v2 are either (1,0),(0,1),(-1,0),(0,-1),(1,1),(-1,1),(-1,-1),(1,-1)
# be careful vector as x^ component first!!!
    
            sdelt=abs(delti)+abs(deltj) # sum of |delti|+|deltj|
            sdelt=int(sdelt)
            deno=max(0.1,abs(delti))
            av=delti/deno
            deno=max(0.1,abs(deltj))
            bv=deltj/deno

# width is analysed if sdelt=1, 2 or 4. These corresponds to vectors v along 
# x^, y^ or at 45 deg.

            if (sdelt == 1 or sdelt == 2 or sdelt == 4 and dist[j,i] > mindist):
                av1=int(-bv) # v1 and v2 are found by rotating v by +-90 deg
                bv1=int(av)
                av2=int(bv)
                bv2=int(-av)
                LKFepsmax=eps_tot[j,i]
                target=frac*LKFepsmax

# set initial values (overwritten if found while s < dsearch)

                idelta=int(dsearch*av1)
                jdelta=int(dsearch*bv1)
                halfw1[n]=np.sqrt(idelta**2 + jdelta**2)
                idelta=int(dsearch*av2)
                jdelta=int(dsearch*bv2)
                halfw2[n]=np.sqrt(idelta**2 + jdelta**2)

# along v1
                s=0
                while s < dsearch:
                    idelta=int((s+1)*av1)
                    jdelta=int((s+1)*bv1)
                    jj=j+jdelta
                    ii=i+idelta
                    if eps_tot[jj,ii] < target:
                        halfw1[n]=np.sqrt(idelta**2 + jdelta**2)
                        break
                    s=s+1

# along v2
                s=0
                while s < dsearch: 
                    idelta=int((s+1)*av2)
                    jdelta=int((s+1)*bv2)
                    jj=j+jdelta
                    ii=i+idelta
                    if eps_tot[jj,ii] < target:
                        halfw2[n]=np.sqrt(idelta**2 + jdelta**2)
                        break
                    s=s+1        

#        tpcalc= np.sqrt(zlkf[n,4]**2 + zlkf[n,5]**2)
#        print(tpcalc) # tpcalc should be equal tp LKFepsmax...it is        
        
            else:
                halfw1[n]=np.nan
                halfw2[n]=np.nan

        zlkf=np.c_[zlkf, halfw1] # add halfw vectors to zlkf
        zlkf=np.c_[zlkf, halfw2]
        
        out_lkfs.append(zlkf)

        l=l+1

#----- save output file -----

    np.save(path_fileout,out_lkfs,allow_pickle=True)

#----  lkf_concatenate_width --------------------------------
#
# Concatenate half widths of a given LKF file in two vectors.
# 
#------------------------------------------------------------

def lkf_concatenate_width (date,path_filein, hwidth):
    
# ilkf[n,7] = hwidth1
# ilkf[n,8] = hwidth2

    print(date)
    tpvect=[]
    l=0
    lt=0
    lr=0
    lkfs = np.load(path_filein,allow_pickle=True)
            
    for i in range(len(lkfs)) :
        ilkf=lkfs[i]
        nb=ilkf.shape[0] # nb of points in LKF i

        for n in range(nb):
            lt=lt+1
            if hwidth == 1:
                if ilkf[n,7] > 0:
                    tpvect.append(ilkf[n,7])
                    l=l+1
                else:
                    lr=lr+1
            elif hwidth == 2:
                if ilkf[n,8] > 0:
                    tpvect.append(ilkf[n,8])
                    l=l+1
                else:
                    lr=lr+1
                    
            else:
                print('wrong hwidth value') 

    print('final number of LKF points:')
    print(l)
    print('number of rejected LKF points:')
    print(lr)
    
    return tpvect

#----  lkf_density ------------------------------------------
#
# Called by driver_lkf_density to calculate contribution 
# to density from a single LKF file (containing many detected
# LKFs). There is no criterion applied here for the distance 
# to land. This could be done later when plotting the density. 
#
#------------------------------------------------------------

def lkf_density(date,creggrid,path_filein):
    
    print('working on date:')
    print(date)

#----- open npy file -----

    lkfs = np.load(path_filein,allow_pickle=True)
    print(lkfs.shape)

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
        nx=528
        ny=735
        jshift=329
        ishift=93
    elif (creggrid == 'creg12'):
        nx=1580
        ny=2198
        jshift=985
        ishift=278
    else:
        print ("Wrong choice of grid")

#---- calc density contribution from group of LKFs -----

    TPdens= np.zeros((ny,nx))

    l=0
    for ilkf in lkfs:
        nb=ilkf.shape[0] # nb of points in LKF i
        zlkf=ilkf

        for n in range(nb):

            jl = int(zlkf[n,0])
            il = int(zlkf[n,1])
            j=jl+jshift-1
            i=il+ishift-1 
            TPdens[j,i]=TPdens[j,i]+1.0
        l=l+1

    return TPdens


#------------------------------------------------------------
#  Functions for lkf_pairs_and_angles
#------------------------------------------------------------

#---- identify type of intersection -------------------------

def identify_int(index1,nb1,index2,nb2):
# index1 and index 2 identify element closest to intersection pt
    if index1<=1 or index2<=1 or index1>=nb1-2 or index2>=nb2-2:
        int_type=2 # T or Y intersecting LKFs
    else:
        int_type=1 # X intersecting LKFs...possible conjugate faults    

    return int_type

#-- mean and more info for vorticity close to intersection --

def get_vort_info(vortint):
# values of vort1 and vort2 are = vort_val=0 at start and end. 
# it does not matter as this does not change if mean is + or -
    meanvort=np.mean(vortint)
    ntp=vortint.shape[0]
    
    nsame=0
    nzero=0
    ntot=0
    for n in range(ntp):
        if vortint[n] == 0.0:
            nzero=nzero+1
        else:
            ntot=ntot+1
            if np.sign(vortint[n]) == np.sign(meanvort):
                nsame=nsame+1

    perc=nsame*100.0/(ntot)

    return meanvort,perc

#---- calculate intersection angle --------------------------

def calc_int_angle(ptype1,coeff1,ptype2,coeff2):
    m1=coeff1[0]
    m2=coeff2[0]
    minval=1e-12    

    if ptype1==1 and ptype2==2:
        denom=max(minval,abs(m2))
        if np.sign(m2) == 0:
            sfact=1.0
        else:
            sfact=np.sign(m2)
        m2=sfact*1.0/denom # convert dx/dy to -dy/dx 
    elif ptype1==2 and ptype2==1:
        denom=max(minval,abs(m1))
        if np.sign(m1) == 0:
            sfact=1.0
        else:
            sfact=np.sign(m1)
        m1=sfact*1.0/denom # convert dx/dy to -dy/dx 
 
    deno=max(minval,abs(1+m1*m2)) # avoid div by zero
    int_angle=np.arctan(abs((m1-m2)/deno))
    int_angle = int_angle*180/np.pi # convert to deg

    return int_angle

def calc_conj_angle(ptype1,coeff1, mvort1int,ptype2,coeff2, mvort2int):
    m1=coeff1[0]
    m2=coeff2[0]
    minval=1e-12    

    if ptype1==1 and ptype2==2:
        denom=max(minval,abs(m2))
        if np.sign(m2) == 0:
            sfact=1.0
        else:
            sfact=np.sign(m2)
        m2=sfact*1.0/denom # convert dx/dy to -dy/dx 
    elif ptype1==2 and ptype2==1:
        denom=max(minval,abs(m1))
        if np.sign(m1) == 0:
            sfact=1.0
        else:
            sfact=np.sign(m1)
        m1=sfact*1.0/denom # convert dx/dy to -dy/dx 
 
    if mvort1int >= 0 :
        mplus=m1 # slope of LKF with positive vort
        mminus=m2 # slope of LKF with negative vort
    else:
        mplus=m2 # slope of LKF with positive vort
        mminus=m1 # slope of LKF with negative vort
        
    # conj angle measured counterclockwise from positive vort LKF to negative one 
    # phiplus and phiminus are postive angles measured from the x axis

    if mplus >= 0 :
        if mminus >= 0:
            if mplus <= mminus : # top right quadrant acute
                phiplus=math.atan(mplus)*180/np.pi # convert to deg
                phiminus=math.atan(mminus)*180/np.pi # convert to deg
                angle_tp = phiminus - phiplus
            elif mplus > mminus : # top right quadrant obtuse
                phiplus=math.atan(mplus)*180/np.pi # convert to deg
                phiminus=math.atan(mminus)*180/np.pi # convert to deg
                angle_tp = 180 -  phiplus + phiminus 
        
        elif mminus < 0: # top quadrants acute or obtuse
            phiplus=math.atan(mplus)*180/np.pi # convert to deg
            phiminus=-1.0*math.atan(mminus)*180/np.pi # convert to deg
            angle_tp = 180 - ( phiplus + phiminus )

    elif mplus < 0 :
        if mminus >= 0: # right quadrants acute or obtuse
            phiplus=-1.0*math.atan(mplus)*180/np.pi # convert to deg
            phiminus=math.atan(mminus)*180/np.pi # convert to deg
            angle_tp = phiplus + phiminus

        elif mminus < 0: 
            if mplus <= mminus : # bottom right quadrant acute
                phiplus=-1.0*math.atan(mplus)*180/np.pi # convert to deg
                phiminus=-1.0*math.atan(mminus)*180/np.pi # convert to deg
                angle_tp = phiplus - phiminus

            elif mplus > mminus : # bottom right quadrant obtuse
                phiplus=-1.0*math.atan(mplus)*180/np.pi # convert to deg
                phiminus=-1.0*math.atan(mminus)*180/np.pi # convert to deg
                angle_tp = 180 - phiminus + phiplus

    return angle_tp

#---- check if two rectangles overlap -----------------------

def overlap(ibl1, jbl1, itr1, jtr1, ibl2, jbl2, itr2, jtr2):
    if itr1 < ibl2 or ibl1 > itr2 or jtr1 < jbl2 or jbl1 > jtr2:
        ovlflag=False
    else:
        ovlflag=True

    return ovlflag

#---- get i,j at intersection point -----------------------

def get_ij_intersection(intersec):
    if intersec.geom_type == 'Point':
        iint=intersec.x
        jint=intersec.y
        clean_int=True
    elif intersec.geom_type == 'LineString': #take 1st pt of string
        iint=intersec.xy[0][0]
        jint=intersec.xy[1][0]
        clean_int=True
    elif intersec.geom_type == 'MultiPoint': #take 1st pt of multipt
        iint=intersec.geoms[0].x
        jint=intersec.geoms[0].y
        clean_int=False
    else:
        iint=intersec.geoms[0].xy[0][0]
        jint=intersec.geoms[0].xy[1][0]
        clean_int=False

    return iint,jint,clean_int

#-- x,y coordinates (in km) of LKF points around mid-point --

def xy_coor(imid,jmid,i1,j1,nmin,nmax,DX,DY,ishift,jshift) :

    print('in new function')

#    j=jl+jshift-1
#    i=il+ishift-1 

#---- polyfit over intersection zone ------------------------

def get_polyfit(vari, varj, xf, yf, pdeg):
    if vari >= varj: # y=p(x)
        coeff = np.polyfit(xf,yf,pdeg)
        yfunc = np.poly1d(coeff)
        xpf = np.linspace(xf[0],xf[-1],50)
        ypf=yfunc(xpf)
        ptype=1
    else:
        coeff = np.polyfit(yf,xf,pdeg) # x=p(y)
        xfunc = np.poly1d(coeff)
        ypf = np.linspace(yf[0],yf[-1],50)
        xpf=xfunc(ypf)
        ptype=2
        
    return xpf,ypf,ptype,coeff

#---- add extra pt at start --------------------------------

def extra_pt_start(i0, i1, j0, j1):
    delti=i1-i0
    deltj=j1-j0
    ist=i0-delti
    jst=j0-deltj
        
    return ist,jst

def extra_pt_end(im1, im2, jm1, jm2):
    delti=im1-im2
    deltj=jm1-jm2
    iend=im1+delti
    jend=jm1+deltj
        
    return iend,jend

#----  lkf_pairs_and_angles ---------------------------------
#
# Identifies pairs of LKFs that intersect and calc the 
# intersection angle. 
#
#------------------------------------------------------------

def lkf_pairs_and_angles(date,creggrid,path_filein,data_pathnc,fileout1,fileout2,dlt):
    
    print('working on date:')
    print(date)

#--- define parameters ---

    vort_val=0.0 # value used to extrapolate vort at both ends of LKF
    pdeg=1 # degree of polynomial for fit

#----- open npy file -----

    lkfs = np.load(path_filein,allow_pickle=True)
    print(lkfs.shape)

#----- open netcdf file --

    creg_nc = xr.open_dataset(data_pathnc)
    vort = creg_nc.vort[0,:,:]/100.0

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
        nx=528
        ny=735
        jshift=329
        ishift=93
    elif (creggrid == 'creg12'):
        nx=1580
        ny=2198
        jshift=985
        ishift=278
    else:
        print ("Wrong choice of grid")

#---- create empty lists ----------------------

    ilkf1lt=[] # lt for list
    ilkf2lt=[]
    nb1lt=[]
    nb2lt=[]
    clean_intlt=[]
    int_anglelt=[]
    int_typelt=[]
    perc1lt=[]
    perc2lt=[]
    mvort1intlt=[]
    mvort2intlt=[]
    conjpairlt=[]
    conjanglt=[]

    xangle1lt=[]
    yangle1lt=[]
    minangle1lt=[]
    xangle2lt=[]
    yangle2lt=[]
    minangle2lt=[]

#---- identify pairs of intersecting LKFs -----

# ilkf1: index of 1st intersecting lkf among n detected lkfs
# ilkf2: index of 2nd intersecting lkf among n detected lkfs
# index1: index along (extended) ilkf1 detected 1kf
# index2: index along (extended) ilkf2 detected 1kf

    for ilkf1, lkf1 in enumerate(lkfs):
        nb1short=lkf1.shape[0] # true nb of points in LKF
        maxj1=np.max(lkf1[:,0])
        minj1=np.min(lkf1[:,0])
        maxi1=np.max(lkf1[:,1])
        mini1=np.min(lkf1[:,1])
        j1=lkf1[:,0]
        i1=lkf1[:,1]

        #--- vorticity along LKF1 ---
        vort1=np.zeros(nb1short)
        for n1 in range(nb1short):
            jj=int(j1[n1])+jshift-1
            ii=int(i1[n1])+ishift-1
            vort1[n1]=vort[jj,ii]

        #--- extrapolate vort1 by one pt on both sides to match shape of j1ext,i1ext ---
        vort1=np.append(vort_val,vort1) # start
        vort1=np.append(vort1,vort_val) # end

        #line1=LineString(np.column_stack((i1,j1)))
        
        #--- extrapolate LKF1 by one pt on both sides ---
        ist,jst=extra_pt_start(i1[0], i1[1], j1[0], j1[1])
        j1ext=np.append(jst,j1)
        i1ext=np.append(ist,i1)

        iend,jend=extra_pt_end(i1[-1], i1[-2], j1[-1], j1[-2])
        j1ext=np.append(j1ext,jend)
        i1ext=np.append(i1ext,iend)
        nb1=i1ext.shape[0] # nb of pts (including extra pts) in LKF1
        line1ext=LineString(np.column_stack((i1ext,j1ext)))

        for ilkf2, lkf2 in enumerate(lkfs):
            if ilkf2 > ilkf1:
                nb2short=lkf2.shape[0] # true nb of points in LKF
                maxj2=np.max(lkf2[:,0])
                minj2=np.min(lkf2[:,0])
                maxi2=np.max(lkf2[:,1])
                mini2=np.min(lkf2[:,1])
#                ovlflag=overlap(mini1, minj1, maxi1, maxj1, mini2, minj2, maxi2, maxj2)
                ovlflag=overlap(mini1-1, minj1-1, maxi1+1, maxj1+1, mini2-1, minj2-1, maxi2+1, maxj2+1)
                if ovlflag:
                    j2=lkf2[:,0]
                    i2=lkf2[:,1]
                    #line2=LineString(np.column_stack((i2,j2)))
                    
                    #--- extrapolate LKF1 by one pt on both sides ---
                    ist,jst=extra_pt_start(i2[0], i2[1], j2[0], j2[1])
                    j2ext=np.append(jst,j2)
                    i2ext=np.append(ist,i2)

                    iend,jend=extra_pt_end(i2[-1], i2[-2], j2[-1], j2[-2])
                    j2ext=np.append(j2ext,jend)
                    i2ext=np.append(i2ext,iend)
                    nb2=i2ext.shape[0] # nb of pts (including extra pts) in LKF2
                    line2ext=LineString(np.column_stack((i2ext,j2ext)))

                    #intersec=line1.intersection(line2) # inters. pt between line1,2
                    intersec=line1ext.intersection(line2ext) # inters. pt between line1,2

                    if not intersec.is_empty:
                        iint,jint,clean_int=get_ij_intersection(intersec) # get i,j at intersection point
                        deltai=abs(i1ext-iint) # delta i between i1 and intersec i
                        deltaj=abs(j1ext-jint) # delta j between j1 and intersec j
                        index1=np.argmin(deltai+deltaj)
                        deltai=abs(i2ext-iint) # delta i between i2 and intersec i
                        deltaj=abs(j2ext-jint) # delta j between j2 and intersec j
                        index2=np.argmin(deltai+deltaj)
                        
                        #--- define part of array close to intersec for polyfit
                        min_ind1=max(0, index1-dlt)
                        max_ind1=min(index1+dlt,nb1-1)
                        xf1=i1ext[min_ind1:max_ind1+1]
                        yf1=j1ext[min_ind1:max_ind1+1]
                        vari1=max(xf1)-min(xf1) # variation of i1 in pts used for polyfit                    
                        varj1=max(yf1)-min(yf1)

                        xpf1,ypf1,ptype1,coeff1=get_polyfit(vari1,varj1,xf1,yf1,pdeg) # polyfit LKF1
      
                        min_ind2=max(0, index2-dlt)
                        max_ind2=min(index2+dlt,nb2-1)
                        xf2=i2ext[min_ind2:max_ind2+1]
                        yf2=j2ext[min_ind2:max_ind2+1]
                        vari2=max(xf2)-min(xf2) # variation of i2 in pts used for polyfit
                        varj2=max(yf2)-min(yf2)

                        xpf2,ypf2,ptype2,coeff2=get_polyfit(vari2,varj2,xf2,yf2,pdeg) # polyfit LKF2
                        
                        #--- identify if intersection is X, T or Y
                        int_type=identify_int(index1,nb1,index2,nb2)
                        
                        #--- calc intersection angle (returns acute angle)
                        int_angle=calc_int_angle(ptype1,coeff1,ptype2,coeff2)
                        
                        #--- lkf1 calc angle with respect to x (or i) axis ---
                        ptypeTP=1 #y=mx+b=b
                        coeffTP=np.zeros(2)  #coeffTP[0]=m=0, coeffTP[1]=0 #not used
                        anglex1=calc_int_angle(ptype1,coeff1,ptypeTP,coeffTP)

                        #--- lkf1 calc angle with respect to y (or j) axis ---
                        ptypeTP=2 #x=my+b
                        coeffTP=np.zeros(2)  #coeffTP[0]=m=0, coeffTP[1]=0 #not used
                        angley1=calc_int_angle(ptype1,coeff1,ptypeTP,coeffTP)

                        min_angle1=min(anglex1,angley1)

                        #--- lkf2 calc angle with respect to x (or i) axis ---
                        ptypeTP=1 #y=mx+b=b
                        coeffTP=np.zeros(2)  #coeffTP[0]=m=0, coeffTP[1]=0 #not used
                        anglex2=calc_int_angle(ptype2,coeff2,ptypeTP,coeffTP)

                        #--- lkf2 calc angle with respect to y (or j) axis ---
                        ptypeTP=2 #x=my+b
                        coeffTP=np.zeros(2)  #coeffTP[0]=m=0, coeffTP[1]=0 #not used
                        angley2=calc_int_angle(ptype2,coeff2,ptypeTP,coeffTP)

                        min_angle2=min(anglex2,angley2)

                        if int_type==1: # possible conjugate fault lines
                            #--- vorticity along LKF2 ---
                            vort2=np.zeros(nb2short)
                            for n2 in range(nb2short):
                                jj=int(j2[n2])+jshift-1
                                ii=int(i2[n2])+ishift-1
                                vort2[n2]=vort[jj,ii]

                            #--- extrapolate vort1 by one pt on both sides to match shape of j1ext,i1ext ---
                            vort2=np.append(vort_val,vort2) # start
                            vort2=np.append(vort2,vort_val) # end

                            #--- define part of vort arrays close to intersec for calc of mean vort
                            vort1int=vort1[min_ind1:max_ind1+1]
                            vort2int=vort2[min_ind2:max_ind2+1]

                            #--- calc mean vort and percentage of pts with same sign as mean vort
                            mvort1int,perc1=get_vort_info(vort1int)
                            mvort2int,perc2=get_vort_info(vort2int)

                            conjpair=False
                            conjangle=np.nan
                            if np.sign(mvort1int) != np.sign(mvort2int):
                                if clean_int:
                                    conjpair=True
                                    conjangle=calc_conj_angle(ptype1,coeff1, mvort1int,ptype2,coeff2, mvort2int)
                                    #print('conj',ilkf1,ilkf2,conjangle, ptype1, ptype2,mvort1int,mvort2int)
                        
                        elif int_type==2:
                            perc1=np.nan
                            perc2=np.nan
                            mvort1int=np.nan
                            mvort2int=np.nan
                            conjpair=False
                            conjangle=np.nan
                            
                        #--- append values in lists
                        
                        ilkf1lt.append(ilkf1)
                        ilkf2lt.append(ilkf2)
                        nb1lt.append(nb1short)
                        nb2lt.append(nb2short)
                        clean_intlt.append(clean_int)
                        int_anglelt.append(int_angle)
                        int_typelt.append(int_type)
                        perc1lt.append(perc1)
                        perc2lt.append(perc2)
                        mvort1intlt.append(mvort1int)
                        mvort2intlt.append(mvort2int)
                        conjpairlt.append(conjpair)
                        conjanglt.append(conjangle)

                        xangle1lt.append(anglex1)
                        yangle1lt.append(angley1)
                        minangle1lt.append(min_angle1)
                        xangle2lt.append(anglex2)
                        yangle2lt.append(angley2)
                        minangle2lt.append(min_angle2)

                        # For DEBUG ---------------------------------
                        cc=1
                        figg=1
                        if ilkf1 == 192 and ilkf2 == 20100:
                            print('int angle=', int_angle)
                            print('ptype',ptype1,ptype2,int_type)
                            print(index1,nb1,index2,nb2)
                            print(coeff1[0], coeff2[0])
                            print('angle',int_angle)
                            print('conj angle',conjangle,180-conjangle)
                            print('min angle grid',min_angle1,min_angle2)
                            print('ilkf1',min_ind1,index1,max_ind1,nb1)
                            print('ilkf2',min_ind2,index2,max_ind2,nb2)
                            print('clean intersect=',clean_int)
                            if figg==1:
                                plt.plot(i1ext,j1ext,'.m')
                                plt.plot(line1ext.xy[0],line1ext.xy[1], '-m')
                                plt.plot( xpf1,ypf1,'g')
                                plt.plot(i2ext,j2ext,'*b')
                                plt.plot(line2ext.xy[0],line2ext.xy[1], '-b')
                                plt.plot( xpf2,ypf2,'orange')
                                if clean_int:
                                    plt.plot( intersec.x,intersec.y, 'sr')
                                if cc==1:
                                    plt.xlim(iint-10, iint+10)
                                    plt.ylim(jint-10, jint+10)
                                plt.show()
                            elif figg==2:
                                maxjtp=int(max(maxj1,maxj2))
                                minjtp=int(min(minj1,minj2))
                                maxitp=int(max(maxi1,maxi2))
                                minitp=int(min(mini1,mini2))
                                # shift indices from local grid to creg grid
                                maxj=maxjtp+jshift-1
                                minj=minjtp+jshift-1
                                maxi=maxitp+ishift-1
                                mini=minitp+ishift-1
                                print(minj,maxj,mini,maxi)
                                print('ptype1',ptype1,mvort1int)
                                print('ptype2',ptype2,mvort2int)
                                for n1 in range(nb1short):
                                    jj=int(j1[n1])+jshift-1
                                    ii=int(i1[n1])+ishift-1
                                    if mvort1int > 0 :
                                        vort[jj,ii]=2
                                    else :
                                        vort[jj,ii]=-2
                    
                                for n2 in range(nb2short):
                                    jj=int(j2[n2])+jshift-1
                                    ii=int(i2[n2])+ishift-1
                                    if mvort2int > 0 :
                                        vort[jj,ii]=4
                                    else :
                                        vort[jj,ii]=-4
                                    
                                vortpc=vort[minj:maxj,mini:maxi]
                                plt.pcolor(vortpc)
                                plt.colorbar()
                                #plt.savefig('testing12.png')
                                plt.show()


#--- create the panda dataframe for output file 1 (angle at int)

    df = pd.DataFrame(ilkf1lt, columns=['ilkf1'])
    df.insert(1, 'ilkf2', ilkf2lt)
    df.insert(2, 'nb1', nb1lt)
    df.insert(3, 'nb2', nb2lt)
    df.insert(4, 'clean_int', clean_intlt)
    df.insert(5, 'int_angle', int_anglelt)
    df.insert(6, 'int_type', int_typelt)
    df.insert(7, 'perc1', perc1lt)
    df.insert(8, 'perc2', perc2lt)
    df.insert(9, 'mean_vort1', mvort1intlt)
    df.insert(10, 'mean_vort2', mvort2intlt)
    df.insert(11, 'conj_pair', conjpairlt)
    df.insert(12, 'conj_angle', conjanglt)
    df.to_csv(fileout1, index=False)

#--- create the panda dataframe for output file 2 (angle with grid at int pt)

    df1 = pd.DataFrame(ilkf1lt, columns=['ilkf1'])
    df1.insert(1, 'ilkf2', ilkf2lt)
    df1.insert(2, 'nb1', nb1lt)
    df1.insert(3, 'nb2', nb2lt)
    df1.insert(4, 'x_angle1', xangle1lt)
    df1.insert(5, 'y_angle1', yangle1lt)
    df1.insert(6, 'min_angle1', minangle1lt)
    df1.insert(7, 'x_angle2', xangle2lt)
    df1.insert(8, 'y_angle2', yangle2lt)
    df1.insert(9, 'min_angle2', minangle2lt)
    df1.insert(10, 'conj_pair', conjpairlt)
    df1.to_csv(fileout2, index=False)

#----  lkf_angles_with_grid ---------------------------------
#
# Calculate angle of LKF with grid at mid LKF point
#
#------------------------------------------------------------

def lkf_angles_with_grid(date,grid_path,path_filein,fileout,dlt,ishift,jshift):
    
    print('working on date:')
    print(date)

#--- define parameters ---

    pdeg=1 # degree of polynomial for fit

#--- open grid file ------

    grid_nc = xr.open_dataset(grid_path)
    DX = grid_nc['e1t']/1000.0 # km
    DY = grid_nc['e2t']/1000.0 # km

#----- open npy file -----

    lkfs = np.load(path_filein,allow_pickle=True)
    print(lkfs.shape)

#---- create empty lists ----------------------

    ilkf1lt=[] # lt for list
    nb1lt=[]
    xanglelt=[]
    yanglelt=[]
    minanglelt=[]

#---- loop through detected LKFs --------------

    for ilkf1, lkf1 in enumerate(lkfs):
        nb1=lkf1.shape[0]
        j1=lkf1[:,0]
        i1=lkf1[:,1]
        
        #--- find mid-point of LKF ---
        nmid=int(np.floor(nb1/2))

        #--- find start and end of LKF for polyfit ---
        nmin=max(0, nmid-dlt)
        nmax=min(nmid+dlt,nb1-1)

        #--- form x(or i) and y(or j) vectors for polyfit ---
        xf1=i1[nmin:nmax+1] # note that xf1=i1[n1,n2] uses in fact i1[n1,n2-1]
        yf1=j1[nmin:nmax+1]
        
        #--- var of xf1 and yf1 vectors to decide type (y=f(x) or =f(y) polyfit ---
        vari1=max(xf1)-min(xf1) # variation of i1 in pts used for polyfit                    
        varj1=max(yf1)-min(yf1)

        #--- x,y coordinates [km] of points in region around mid-point ---
#        if ilkf1 == 9500:
#            xc,yc=xy_coor(imid,jmid,i1,j1,nmin,nmax,DX,DY,ishift,jshift)

        #--- get polyfit in region around mid-point ---
        xpf1,ypf1,ptype1,coeff1=get_polyfit(vari1,varj1,xf1,yf1,pdeg) # polyfit LKF1
        
        #--- calc angle with respect to x (or i) axis ---
        ptype2=1 #y=mx+b=b
        coeff2=np.zeros(2)  #coeff2[0]=m=0, coeff2[1]=0 #not used
        anglex=calc_int_angle(ptype1,coeff1,ptype2,coeff2)

        #--- calc angle with respect to y (or j) axis ---
        ptype2=2 #x=my+b
        coeff2=np.zeros(2)  #coeff2[0]=m=0, coeff2[1]=0 #not used
        angley=calc_int_angle(ptype1,coeff1,ptype2,coeff2)

        min_angle=min(anglex,angley)

        #--- define y=cte aligned with x axis for plotting ---
        if ilkf1 == 9500:
            nmin=max(0, nmid-dlt-dlt)
            nmax=min(nmid+dlt+dlt,nb1-1)
            xref=i1[nmin:nmax+1]
            ntp=xref.shape[0]
            yref=np.zeros(ntp)
            yref[:]=j1[nmid]
            plt.plot(i1,j1, 'c')
            plt.plot(xf1,yf1, '.b')
            plt.plot(xpf1,ypf1,'orange')
            plt.plot(xref,yref,'r')
            plt.show()

        #--- append values in lists
                        
        ilkf1lt.append(ilkf1)
        nb1lt.append(nb1)
        xanglelt.append(anglex)
        yanglelt.append(angley)
        minanglelt.append(min_angle)

#--- create the panda dataframe for output file

    df = pd.DataFrame(ilkf1lt, columns=['ilkf1'])
    df.insert(1, 'nb1', nb1lt)
    df.insert(2, 'x_angle', xanglelt)
    df.insert(3, 'y_angle', yanglelt)
    df.insert(4, 'min_angle', minanglelt)
    df.to_csv(fileout, index=False)

#------------------------------------------------------------
#  Functions for lkf_length
#------------------------------------------------------------

def haversine(re,lat1, lon1, lat2, lon2):
    '''
    Calcule la distance entre deux points sur la sphere (terre)
    :param lat1: latitude du premier point
    :param lon1: longitude du premier point
    :param lat2: latitude du deuxieme point
    :param lon2: longitude du deuxieme point
    :return: distance en metres
    '''
    #lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    lat1=lat1*np.pi/180.0 # convert to rad
    lat2=lat2*np.pi/180.0 # convert to rad
    lon1=lon1*np.pi/180.0 # convert to rad
    lon2=lon2*np.pi/180.0 # convert to rad
    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return c * re

#----  lkf_length -------------------------------------------
#
# Calculate length of LKF. There is no polynomial fit used. 
# The length is calculated from one pixel to the next using 
# the haversine formula.
#
#------------------------------------------------------------

def lkf_length(date,creggrid,path_filein,fileout):
    
    print('working on date:')
    print(date)

#--- define parameters ---

    Rearth = 6371.0  # Radius of earth in kilometers

#----- open npy file -----

    lkfs = np.load(path_filein,allow_pickle=True)
    print(lkfs.shape)

#---- create empty lists ----------------------

    ilkf1lt=[] # lt for list
    nb1lt=[]
    lengthlt=[]

#---- calc lengths of all LKFs in input file -----

    for ilkf1, lkf1 in enumerate(lkfs):
        nb1=lkf1.shape[0]
        lat=lkf1[:,3]
        lon=lkf1[:,2]

        length=0.0 # initialize
        for n in range(nb1-1): # last dlength is from n=nb1-2 to n+1=nb1-1
            lat1=lat[n]
            lon1=lon[n]
            lat2=lat[n+1]
            lon2=lon[n+1]

            dlength=haversine(Rearth,lat1, lon1, lat2, lon2)
            length=length+dlength

        #--- append values in lists
        ilkf1lt.append(ilkf1)
        nb1lt.append(nb1)
        lengthlt.append(length)

#--- create the panda dataframe for output file

    df = pd.DataFrame(ilkf1lt, columns=['ilkf1'])
    df.insert(1, 'nb1', nb1lt)
    df.insert(2, 'length', lengthlt)
    df.to_csv(fileout, index=False)
