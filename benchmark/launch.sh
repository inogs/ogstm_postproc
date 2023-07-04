#! /bin/bash

module load autoload
module load intel/oneapi-2021--binary
module load intelmpi/oneapi-2021--binary
module load mkl/oneapi-2021--binary
module load netcdf/4.7.4--oneapi--2021.2.0-ifort
module load netcdff/4.5.3--oneapi--2021.2.0-ifort
source /g100_work/OGS21_PRACE_P/COPERNICUS/py_env_3.6.8/bin/activate


export CINECA_WORK=/g100_work/OGS_devC
export OPA_HOME=Benchmark/HC
BITSEA=$CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC/bit.sea
export PYTHONPATH=:$BITSEA
HERE=$PWD

export ONLINE_REPO=/g100_work/OGS_devC/V10C/RUNS_SETUP/ONLINE

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/
 BASEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/PROFILATORE/

sed -e "s%\@\@INPUTDIR\@\@%${INPUTDIR}%g" -e "s%\@\@BASEDIR\@\@%${BASEDIR}%g " profiler.tpl > $HERE/profiler.py
cd $CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC

if [[ -d bit.sea ]] ; then
    echo "Nothing to do"
else
    git clone git@github.com:inogs/bit.sea.git
    
    cd $BITSEA/validation/deliverables
    cp $HERE/profiler.py .
    python profiler.py
fi

# 1. sbatch job.POST.slurm.galileo
# 2. sbatch job.serial.slurm

