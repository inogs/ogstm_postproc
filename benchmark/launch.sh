#! /bin/bash

module load autoload
module load intel/oneapi-2021--binary
module load intelmpi/oneapi-2021--binary
module load mkl/oneapi-2021--binary
module load netcdf/4.7.4--oneapi--2021.2.0-ifort
module load netcdff/4.5.3--oneapi--2021.2.0-ifort
source /g100_work/OGS21_PRACE_P/COPERNICUS/py_env_3.6.8/bin/activate


#  user settings #########################
export CINECA_WORK=/g100_work/OGS_devC
export OPA_HOME=Benchmark/HC
# EDIT spaghetti_plot_user_setting.txt
##########################################


BITSEA=$CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC/bit.sea
export PYTHONPATH=:$BITSEA
HERE=$PWD

export ONLINE_REPO=/g100_work/OGS_devC/V10C/RUNS_SETUP/ONLINE
export    MASKFILE=/g100_work/OGS_devC/Benchmark/SETUP/PREPROC/MASK/meshmask.nc


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/
 BASEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/PROFILATORE/
PROFILES=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/STAT_PROFILES

sed -e "s%\@\@INPUTDIR\@\@%${INPUTDIR}%g" -e "s%\@\@BASEDIR\@\@%${BASEDIR}%g " profiler.tpl > $HERE/profiler.py
sed -e "s%actual%PROFILES%g " timeseries_user_settings.txt > $HERE/profiles_plotter_user_settings.txt

cp $HERE/profiles_plotter_user_settings.txt $BITSEA/validation/deliverables

cd $CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC

if [[ -d bit.sea ]] ; then
    cd $HERE
else
    git clone git@github.com:inogs/bit.sea.git
    cd $BITSEA/validation/deliverables
    cp $HERE/profiler.py .
    python profiler.py
fi

cd $HERE
export VALIDATION_DIR=$CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC/output/VALIDATION
export VALIDATION_DIR=/g100_work/OGS_devC/Benchmark/pub/HC

# 1. sbatch job.POST.slurm.galileo
# 2. sbatch job.serial.slurm

