#!/bin/bash

#SBATCH --job-name=valid
#SBATCH -N1 -n 1
#SBATCH --time=4:00:00
#SBATCH --account=OGS21_PRACE_P
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

. ../profile.inc
. ./launch.sh

cd $SLURM_SUBMIT_DIR


my_prex_or_die "$BASEDIR/jobProfiler.sh"


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/


STAT_PROFILES_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES/



./sat.sh   #13 min
./maps.sh
./float.sh # 17 min
