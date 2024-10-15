#!/bin/bash

# ord_soumet ./Soumet_driver_LKF_calc_width.sh -cm 10G -w 360 -jn 'lkf_width'

#. ssmuse-sh -p /fs/ssm/eccc/cmd/cmds/env/python/py39_2022.05.24_rhel-8-icelake-64

eval "$(/fs/ssm/main/opt/intelcomp/master/inteloneapi_2022.1.2_multi/oneapi/intelpython/python3.9/bin/conda shell.bash hook)"
conda activate lkf_tools

set -ex

cd /home/jfl001/Lemieux_et_al_plast_pot/lkf_pack_ice_mask

#./lance_calc_dist.sh

python3 -u CREG_driver_LKF_calc_width.py
