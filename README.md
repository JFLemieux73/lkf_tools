# General information
This repository was forked from https://github.com/nhutter/lkf_tools. The detection and tracking algorithms correspond to version 2 of the nhutter repository. Minor modifications were done in lkf_tools/dataset.py to be able to process ECCC CICE outputs. Drivers were also implemented to run the detection algorithm and to calculate LKF metrics for ECCC outputs. 

## LKF analysis tools
We developed our own set of tools to calculate LKF metrics (e.g. LKF density). The Python code for these metrics is in CREG_lkf_tools.py. Most metrics are the same ones used in :

```
Hutter, N. et al. (2022), Sea Ice Rheology Experiment (SIREx): 2. Evaluating linear kinematic features in high-resolution sea
ice simulations. JGR Oceans, 127, e2021JC017666.
https://doi.org/10.1029/2021JC017666.
```
We introduce two new LKF metrics: the LKF width and the angle of LKFs with the axes of the computational grid. These tools were developed for the following article:

```
Lemieux, J.F. et al., Impact of non-normal flow rule on linear kinematic features in pan-Arctic ice-ocean simulations, The Cryosphere, accepted.
```
## Contact

jean-francois.lemieux@ec.gc.ca

