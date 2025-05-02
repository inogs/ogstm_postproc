#!/bin/bash

#SBATCH --job-name=valid
#SBATCH -N1 -n 1
#SBATCH --time=2:00:00
#SBATCH --account=OGS23_PRACE_IT
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

YEAR=2021
. ../profile.inc
. ./config.sh -y $YEAR

cd $SLURM_SUBMIT_DIR

./timeseries.sh # 16m serial
./sat.sh

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/
export STAT_PROFILES_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES/




./maps.sh -y $YEAR   # 5 min
./float.sh           # 17 min
./static.sh -y $YEAR # 10 min
./clean.sh -y $YEAR

./maps_MY.sh -s 2022 -e 2024

