#! /bin/bash

module load autoload
module load intel/oneapi-2021--binary
module load intelmpi/oneapi-2021--binary
module load mkl/oneapi-2021--binary
module load netcdf/4.7.4--oneapi--2021.2.0-ifort
module load netcdff/4.5.3--oneapi--2021.2.0-ifort
source /g100_work/OGS23_PRACE_IT/COPERNICUS/py_env_3.9.18/bin/activate


#Hypotheses:
# 1. data are in $CINECA_SCRATCH (model and postproc)
# 2. $OPA_HOME is path relative to $CINECA_SCRATCH


#  user settings #########################
export OPA_HOME=Benchmark/DA_SAT
#
export VALIDATION_DIR=/g100_work/OGS_devC/Benchmark/pub/Benchmark/DA_SAT  ## the path after pub/ will be published https://medeaf.inogs.it/internal-validation
#
# EDIT timeseries_user_setting.txt
#
export CINECA_WORK=/g100_work/OGS_devC
POSTPROCDIR=$CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC  ## $CINECA_WORK or $CINECA_SCRATCH
##########################################




BITSEA=${POSTPROCDIR}/bit.sea
export PYTHONPATH=$BITSEA
HERE=$PWD

export ONLINE_REPO=/g100_work/OGS_devC/V10C/RUNS_SETUP/ONLINE
export    MASKFILE=/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/
 BASEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/PROFILATORE/
export STATPROFILESDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES

cd $POSTPROCDIR


if [[ -d bit.sea ]] ; then
    cd $HERE
else
    git clone git@github.com:inogs/bit.sea.git
    cd $BITSEA
    git checkout V10C
    cd $BITSEA/validation/deliverables
    sed -e "s%\@\@INPUTDIR\@\@%${INPUTDIR}%g" -e "s%\@\@BASEDIR\@\@%${BASEDIR}%g " $HERE/profiler.tpl > profiler.py
    cp $HERE/VarDescriptorB.xml $BITSEA/postproc
    python profiler.py
fi

cd $HERE


# 1. sbatch job.POST.slurm.galileo # 1h
# 2. sbatch job.serial.slurm       # 1h30

