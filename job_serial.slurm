#!/bin/bash

#SBATCH --job-name=DREScopy
#SBATCH -N1 -n 1
#SBATCH --time=3:00:00
#SBATCH --account=OGS_dev_0
#SBATCH --partition=bdw_all_serial

cd $SLURM_SUBMIT_DIR
date
echo "Archiving on DRES"


cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/DA__FREQ_1/tar/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/DA_DIRS

cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/AVE_FREQ_2_compressed/tar/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/AVE/

cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/AVE_FREQ_1_compressed/tar/2016/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/AVE/DAILY/2016/
date
cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/AVE_FREQ_1_compressed/tar/2017/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/AVE/DAILY/2017/
date
cp /marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/AVE_FREQ_1_compressed/tar/2018/*tar /gss/gss_work/DRES_OGS_BiGe/ateruzzi/EAS/TRANSITION_24/output/AVE/DAILY/2018/
date


