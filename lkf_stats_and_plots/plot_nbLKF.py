import os,sys
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

#----- INPUT -----
#PATH_OUT='/home/jfl001/data/Lemieux2022/LKF_diag/Histo_width'
main_dir='/home/jfl001/data/Lemieux_et_al_plast_pot/LKF_diag_pack'
EXP1='run_eg1p16_ef1p75'
label1='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=1.16'
EXP2='run_eg1p75_ef1p75'
label2='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=1.75'
EXP3='run_eg2p63_ef1p75'
label3='e$_\mathrm{F}$=1.75, e$_\mathrm{G}$=2.63'
year='2005'

suffix=year+'0101_'+year+'0531.npy'
#-----------------

file1=os.path.join(main_dir+'/'+EXP1+'/nbLKFs/number_lkf_'+suffix)
file2=os.path.join(main_dir+'/'+EXP2+'/nbLKFs/number_lkf_'+suffix)
file3=os.path.join(main_dir+'/'+EXP3+'/nbLKFs/number_lkf_'+suffix)

df1 = pd.read_csv(file1, parse_dates=['date'])
df2 = pd.read_csv(file2, parse_dates=['date'])
df3 = pd.read_csv(file3, parse_dates=['date'])

print('mean nb1:', df1['nb_of_LKFS'].mean())
print('mean nb2:', df2['nb_of_LKFS'].mean())
print('mean nb3:', df3['nb_of_LKFS'].mean())

ax = df1.plot(x = 'date', y = 'nb_of_LKFS', color = "dodgerblue")
ax.set_prop_cycle(None)
df2.plot(ax=ax, x = 'date', y = 'nb_of_LKFS', color = "orange")
df3.plot(ax=ax, x = 'date', y = 'nb_of_LKFS', color = "darkviolet")
ax.legend([label1, label2, label3])
ax.set_xlabel("", fontsize='2')
ax.set_ylabel("Nb of LKFs")
ax.set_ylim(0, 280)


fileout='FIGS/Nb_LKFs_ef1p75_'+year+'_pack.png'
plt.savefig(fileout)
plt.show()
