#!/bin/bash

#SBATCH --job-name=valid
#SBATCH -N1 -n 1
#SBATCH --time=2:00:00
#SBATCH --account=OGS23_PRACE_IT
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

YEAR=2022
. ../profile.inc
. ./config.sh -y $YEAR

cd $SLURM_SUBMIT_DIR

./sat.sh
./maps.sh -y $YEAR   # 5 min
./float.sh           # 17 min/year
./static.sh          # 10 min

./maps_MY.sh -s 2022 -e 2024

./clean.sh -y $YEAR
