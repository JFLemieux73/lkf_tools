# General information
This repository was forked from https://github.com/nhutter/lkf_tools. The detection and tracking algorithms correspond to version 2 of the nhutter repository. Minor modifications were done in lkf_tools/dataset.py to be able to process ECCC CICE outputs. The tools currently work for the CREG025 and CREG12 grids (regional ORCA grids). Using another structured grid would require modifications in lkf_metrics.py and in the drivers. 

The main driver is driver_lkf_detect.py. There is no config file. The user simply enters information in the INPUT section of the driver file:  

`grid` is a label to identify the grid of the model.  
`vortflag` specifies whether the netcdf files include vorticity (=1) or not (=2). Note that vorticity is required to identify pairs of conjugate LKFs. 
`EXP` is a label to identify a numerical experiment.  
`main_dirnc` is the path to the directory that contains model netcdf outputs.  
`main_dir_grid` is the path to the directory that contains the model grid.  
`store_main_dirTP` is the path to the directory where LKF diagnostic will be stored.  
`kvalue` is the kernel value for the detection algorithm. Suggested value: 7.  
`produce_plot` set to true creates a figure showing the detected LKFs.  
`pack_ice_mask` set to true causes the algorithm to detect LKFs only inside a mask in the central Arctic. This mask would need to be created for other grids.  
`SDATE` specifies the starting date for the detection algorithm.  
`EDATE` specifies the end date for the detection algorithm.  
`FREQ` specifies the frequency at which the detection is performed. Suggested value: 24H (daily).  
`suffix` is an additional string to specify the names of netcdf files.  

The detection algorithm requires the activation of lkf_tools with conda (enter proper path_to_conda):

eval "$(path_to_conda shell.bash hook)"  
conda activate lkf_tools  

If the detection algorithm fails, it is likely that a path is wrong, that a variable is missing or not named as expected. It shoud be easy to fix these problems either in driver_lkf_detect.py or in lkf_tools/lkf_metrics.py. The model netcdf outputs should contain divergence, shear, concentration and the velocity components. The file for the grid should contain fields for dx, dy, latitude and longitude.  

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

The user must enter input information in the INPUT section of the drivers. Note that many inputs are the same ones already introduced above for driver_lkf_detect.py.  

### driver_lkf_angles_with_grid_at_mid_length.py  

This diagnostic calculates angles of detected LKFs with the computational grid during the period `SDATE`-`EDATE`. These are calculated in a region centered at the mid-point of detected LKFs. 

`delta` defines the number of LKF points on both sides of the mid-point used to calculate the angles. Suggested value: 10.   

### driver_lkf_calc_width.py  

Calculates the width of detected LKFs (in number of pixels) for the period `SDATE`-`EDATE`. 

`dsearch` defines the maximum number of grid cells in all search directions for calculating the width. Suggested value: 5. 
`frac` defines the criterion to determine the LKF width. Suggested value: 0.5   

Note that the calculation of the width needs to be done in two steps. Once  driver_lkf_calc_width.py is done, driver_lkf_concatenate_width.py should be used.  

### driver_lkf_density.py  

Calculates the fraction of times (between 0 and 1) for the period `SDATE`-`EDATE` a grid cell is crossed by a detected LKF  (in number of pixels).

### driver_lkf_length.py  

Calculates the length (in km) of detected LKFs for the period `SDATE`-`EDATE`.  

### driver_lkf_length.py  

Calculates the number of detected LKFs for the period `SDATE`-`EDATE`.  

### driver_lkf_pairs_and_angles.py  

Identifies pairs of conjugate LKFs and calculates the angle of intersection and the angles with the grid. The metrics are calculated for the period `SDATE`-`EDATE`.  

Statistics can then be calculated and plots produced. This can be done using the set of tools in the directory lkf_stats_and_plots.  

## Contact

jean-francois.lemieux@ec.gc.ca

