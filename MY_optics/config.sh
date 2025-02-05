#! /bin/bash

usage() {
echo "Is a config file for automatic postproc, it needs to be edited by user"
echo "SYNOPSIS"
echo "./config.sh -y [ YEAR ] --init "
echo "Prepares som and launches profiler.py"
echo ""
echo "source config.sh"
echo "exports internal settings as a config file" 

}

if [ $# -lt 2 ] ; then
  usage
  exit 1
fi

RUN_PROFILER=0
for I in 1 2 ; do 
	case $1 in
	    -y | --year )
	            YEAR=$2
	            shift 2
	            ;;
	    --init )
	       RUN_PROFILER=1
	       shift 1
	       ;;
	esac
done


module load autoload
module load intel/oneapi-2021--binary
module load intelmpi/oneapi-2021--binary
module load mkl/oneapi-2021--binary
module load netcdf/4.7.4--oneapi--2021.2.0-ifort
module load netcdff/4.5.3--oneapi--2021.2.0-ifort
source /g100_work/OGS23_PRACE_IT/COPERNICUS/py_env_3.9.18_new/bin/activate


#Hypotheses:
# 1. data are in $CINECA_SCRATCH (model and postproc)
# 2. $OPA_HOME is path relative to $CINECA_SCRATCH


#  user settings #########################
export OPA_HOME=V11C/TRANSITION
#
export VALIDATION_DIR=/g100_work/OGS_devC/Benchmark/pub/gbolzon/V11C/TRANSITION  ## the path after pub/ will be published https://medeaf.inogs.it/internal-validation
#
# EDIT timeseries_user_setting.txt
#
export CINECA_WORK=/g100_work/OGS_devC
POSTPROCDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC  ## $CINECA_WORK or $CINECA_SCRATCH
##########################################





BITSEA=${POSTPROCDIR}/bit.sea
export PYTHONPATH=$BITSEA/src/
HERE=$PWD

export ONLINE_REPO=/g100_work/OGS_devC/V11C/TRANSITION/ONLINE



export STATPROFILESDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES


if [ $RUN_PROFILER -eq 1 ] ; then

    cd $POSTPROCDIR
    if  ! [ -d bit.sea ] ; then
        git clone git@github.com:inogs/bit.sea.git
        cd $BITSEA
        git checkout floatsV11C
    fi

fi


# static Validation dirs
export SAT_CHLWEEKLY_DIR=/g100_work/OGS_devC/V11C/TRANSITION/POSTPROC/validation/SAT/CHL/DT/WEEKLY_4_24
export SAT_RRSWEEKLY_DIR=/g100_work/OGS23_PRACE_IT/csoto/rrs_data/V11C/SAT/WEEKLY_24
export SAT_VALID_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/validation/SAT


# 1. sbatch job.POST.slurm.galileo -y 2020 # 2h
# 2. sbatch job.serial.slurm               # 1h30

