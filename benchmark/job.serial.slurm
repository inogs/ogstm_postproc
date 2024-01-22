#!/bin/bash

#SBATCH --job-name=valid
#SBATCH -N1 -n 1
#SBATCH --time=2:00:00
#SBATCH --account=OGS23_PRACE_IT
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

. ../profile.inc
. ./launch.sh

cd $SLURM_SUBMIT_DIR

./timeseries.sh # 2m


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/


export STAT_PROFILES_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES/



./sat.sh   #13 min
./maps.sh  # 5 min
./float.sh # 17 min
./static.sh # 10 min

