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
# EDIT timeseries_user_setting.tpl -- for multirun color settings
#
export CINECA_WORK=/g100_work/OGS_devC
POSTPROCDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC  ## $CINECA_WORK or $CINECA_SCRATCH
##########################################





BITSEA=${POSTPROCDIR}/bit.sea
export PYTHONPATH=$BITSEA/src/
HERE=$PWD

export ONLINE_REPO=/g100_work/OGS_test2528/V12C_QUID/PREPROC/ONLINE
export    MASKFILE=/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/
 BASEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/PROFILATORE/

export STATPROFILESDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES


# Robustness about mv ave files
[[ -f $INPUTDIR/ave.${YEAR}0101-12:00:00.N1p.nc ]] ||  INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/${YEAR}


if [ $RUN_PROFILER -eq 1 ] ; then
    echo "RUN PROFILER=$RUN_PROFILER"
    echo "INPUTDIR=$INPUTDIR"

    YEAR2=$(( YEAR + 1 ))
    cd $POSTPROCDIR
    if  ! [ -d bit.sea ] ; then
        git clone git@github.com:inogs/bit.sea.git
        cd $BITSEA
        git checkout floatsV11C_merged
    fi
    cd $HERE
    # float profiler
    sed -e "s%\@\@INPUTDIR\@\@%${INPUTDIR}%g" -e "s%\@\@BASEDIR\@\@%${BASEDIR}%g " \
        -e "s%\@\@YEAR1\@\@%${YEAR}%g" -e "s%\@\@YEAR2\@\@%${YEAR2}%g "    profiler.tpl > profiler.py
    python profiler.py
#EBASEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/PROFILATORE_EMODNET/
#   Nutrients profiler
#   sed -e "s%\@\@INPUTDIR\@\@%${INPUTDIR}%g" -e "s%\@\@BASEDIR\@\@%${EBASEDIR}%g " \
#       -e "s%\@\@YEAR1\@\@%${YEAR}%g" -e "s%\@\@YEAR2\@\@%${YEAR2}%g "    profiler_RA_N.tpl > profiler_RA_N.py
#    python profiler_RA_N.py
    sed -e "s%actual%${STATPROFILESDIR}%g " $HERE/timeseries_user_settings.tpl > timeseries_user_setting.txt

fi


# static Validation dirs
export SAT_CHLWEEKLY_DIR=/g100_scratch/usera07ogs/a07ogs00/V11C/ONLINE/SAT/CHL/DT/WEEKLY_4_24
export SAT_VALID_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/validation/SAT


# 1. sbatch job.POST.singleyear.slurm -y 2020 # 02:30:00
# 2. sbatch job.serial.slurm                  # 00:30:00

