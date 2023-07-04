#!/bin/bash

#SBATCH --job-name=DREScopy
#SBATCH -N1 -n 1
#SBATCH --time=4:00:00
#SBATCH --account=OGS21_PRACE_P
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

. ../profile.inc
. ./launch.sh

cd $SLURM_SUBMIT_DIR
export    MASKFILE=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/meshmask.nc

$BASEDIR/jobProfiler.sh






