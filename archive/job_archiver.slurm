#!/bin/bash

#SBATCH --job-name=DREScopy
#SBATCH -N1 -n 1
#SBATCH --time=3:00:00
#SBATCH --account=OGS21_PRACE_P
#SBATCH --partition=g100_all_serial

cd $SLURM_SUBMIT_DIR

. ../profile.inc
echo "Archiving on DRES"

my_prex_or_die "cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/DA__FREQ_1/tar/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/DA_DIRS"


my_prex_or_die "cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/AVE_FREQ_1_compressed/tar/2016/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/AVE/DAILY/2016/ "


