#!/bin/bash

#SBATCH --job-name=valid
#SBATCH -N1
#SBATCH --ntasks-per-node=24
#SBATCH --time=00:30:00
#SBATCH --mem=100gb
#SBATCH --account=OGS_devC
#SBATCH --partition=g100_meteo_prod
#SBATCH --qos=qos_meteo


cd $SLURM_SUBMIT_DIR

. ../profile.inc
. ./launch.sh -y 2019

cd $SLURM_SUBMIT_DIR

./timeseries.sh # 2m
./sat.sh   #13 min

exit 0
./maps.sh  # 5 min
./float.sh # 17 min
./static.sh # 10 min
./clean.sh 
