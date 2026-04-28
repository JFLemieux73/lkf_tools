import os,sys
import numpy as np
import matplotlib as mpl
#mpl.use('Agg')
import matplotlib.pyplot as plt

#----- INPUT -----
#col1='b'
#col2='r'
#col3='c'
label1='$e_{F}=1.5$'
label2='$e_{F}$=1.75'
label3='$e_{F}$=2.0'
dsearch=5
#-----------------

dsstr=str(dsearch)

fileout1='FIGS/mean_width_ef_fixed_2005_ds'+dsstr+'_pack.png'
fileout2='FIGS/mean_width_eg_fixed_2005_ds'+dsstr+'_pack.png'

y1=np.zeros(3) # ef=1.5
y2=np.zeros(3) # ef=1.75
y3=np.zeros(3) # ef=2.0
x1=np.zeros(3)
x2=np.zeros(3)
x3=np.zeros(3)

x1[0]=1.0
x1[1]=1.5
x1[2]=2.25

x2[0]=1.16
x2[1]=1.75
x2[2]=2.63

x3[0]=1.33
x3[1]=2.0
x3[2]=3.0

if dsearch == 5:

    y1[0]=3.60 # 1.5
    y1[1]=4.64
    y1[2]=4.49

    y2[0]=3.87 # 1.75
    y2[1]=4.97
    y2[2]=5.06

    y3[0]=4.12 # 2.0
    y3[1]=5.29
    y3[2]=5.58

elif dsearch == 6:

    y1[0]= 0.0 #1.5
#    y1[1]=4.62
#    y1[2]=4.68

#    y2[0]=3.83 # 1.75
#    y2[1]=4.98
#    y2[2]=5.27

#    y3[0]=4.08 # 2.0
#    y3[1]=5.32
#    y3[2]=5.80

plt.figure(1)
plt.plot(x1, y1, marker='o', color = "dodgerblue")
plt.plot(x2, y2, marker='s', color = "orange")
plt.plot(x3, y3, marker='*', color = "darkviolet")
plt.ylim(3, 6)
plt.xlim(0.9, 3.1)
plt.legend([label1, label2, label3], loc ="lower right")
plt.ylabel('Mean LKF width [nb of pixels]', fontsize=12)
plt.xlabel('$e_G$', fontsize=14)
#plt.xticks(x, mylabels)
#plt.locator_params(axis='x', nbins=7)
#plt.xticks(rotation=45)
plt.savefig(fileout1)
#plt.show()

y4=np.zeros(5) # eg=1.75
x4=np.zeros(5)

x4[0]=1.16
x4[1]=1.5
x4[2]=1.75
x4[3]=2.0
x4[4]=2.63

if dsearch == 5:

    y4[0]=3.87
    y4[1]=4.71
    y4[2]=4.97
    y4[3]=4.92
    y4[4]=4.63

elif dsearch == 6:

    y4[0]=3.99
#    y4[1]=4.78
#    y4[2]=4.98
#    y4[3]=4.92
#    y4[4]=4.62

label4='$e_{g}$=1.75'
plt.figure(2)
plt.plot(x4, y4, marker='o')
plt.ylim(3.4, 5.6)
plt.xlim(0.9, 3.1)
plt.legend([label4], loc ="lower right")
plt.ylabel('Mean LKF width [nb of grid cells]', fontsize=12)
plt.xlabel('$e_f$', fontsize=14)
#plt.xticks(x, mylabels)
#plt.locator_params(axis='x', nbins=7)
#plt.xticks(rotation=45)
plt.savefig(fileout2)
plt.show()
