# General information
This repository was forked from https://github.com/nhutter/lkf_tools. The detection and tracking algorithms correspond to version 2 of the nhutter repository. Minor modifications were done in lkf_tools/dataset.py to be able to process ECCC CICE outputs. The tools currently work for the CREG025 and CREG12 grids (regional ORCA grids). A user wanting to use another grid would have to make some modifications in lkf_metrics.py and in the drivers. 

The main driver is driver_lkf_detect.py. There is no config file. The user simply enters inputs in the driver file. 

The detection algorithm requires the activation of lkf_tools with conda (enter proper path_to_conda):

eval "$(path_to_conda shell.bash hook)"  
conda activate lkf_tools  

Once LKFs have been detected with driver_lkf_detect.py, other drivers can be used to analyse these LKFs. 

## LKF analysis tools
We developed our own set of tools to calculate LKF metrics (e.g. LKF density). The Python code for these metrics is in lkf_tools/lkf_metrics.py. Most metrics are the same ones used in :

```
Hutter, N. et al. (2022), Sea Ice Rheology Experiment (SIREx): 2. Evaluating linear kinematic features in high-resolution sea
ice simulations. JGR Oceans, 127, e2021JC017666.
https://doi.org/10.1029/2021JC017666.
```
We introduce two new LKF metrics: the LKF width and the angle of LKFs with the axes of the computational grid. These tools were developed for the following article:

```
Lemieux, J.F. et al. (2025), Impact of non-normal flow rule on linear kinematic features in pan-Arctic ice-ocean simulations. 
The Cryosphere, 19, 10.5194/tc-19-5639-2025.
```

The drivers for the LKF metrics are:

driver_lkf_angles_with_grid_at_mid_length.py  
driver_lkf_calc_width.py  
driver_lkf_concatenate_width.py  
driver_lkf_density.py  
driver_lkf_length.py  
driver_lkf_number.py  
driver_lkf_pairs_and_angles.py  

Statistics can then be calculated and plots produced. This can be done using the set of tools in lkf_stats_and_plots.  

## Contact

jean-francois.lemieux@ec.gc.ca

