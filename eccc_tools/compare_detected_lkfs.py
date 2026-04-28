import numpy as np
import pickle

exp='run_eg1p75_ef1p75'
zdate='2005042500'

dir1='/home/jfl001/data/TESTlkf/storage/LKF_diag/'+exp+'/detectedLKFs/'+zdate+'_'+exp

dir2='/home/jfl001/data/DEVlkfv3/LKF_diag/'+exp+'/detectedLKFs/'+zdate+'_'+exp

file1=dir1+'/lkf_'+zdate+'_'+exp+'_001.npy'
file2=dir2+'/lkf_'+zdate+'_'+exp+'_001.npy'

lkfs1 = np.load(file1,allow_pickle=True)
lkfs2 = np.load(file2,allow_pickle=True)

if lkfs1.shape[0] == lkfs2.shape[0] :
    print('Good!')
else :
    print('shape pas pareil')

#---- create empty lists ----------------------

nb1lt=[]
nb2lt=[]

#---- compare nb of points -----

for ilkf1, lkf1 in enumerate(lkfs1):
    nb1lt.append(lkf1.shape[0])

for ilkf2, lkf2 in enumerate(lkfs2):
    nb2lt.append(lkf2.shape[0])

for i in range(lkfs1.shape[0]):
    n1=nb1lt[i]
    n2=nb2lt[i]
    ndiff=n2-n1
    if ndiff != 0:
        print('nb pas pareil')
