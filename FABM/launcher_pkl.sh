#! /bin/bash

module purge
module load profile/base
module load intel/pe-xe-2018--binary intelmpi/2018--binary
module load autoload
module load hdf5/1.8.18--intel--pe-xe-2018--binary netcdf/4.6.1--intel--pe-xe-2018--binary
module load mpi4py/3.0.0--intelmpi--2018--binary
source /gpfs/work/OGS20_PRACE_P/COPERNICUS/py_env_2.7.12/bin/activate
export PYTHONPATH=$PYTHONPATH:/gpfs/work/OGS20_PRACE_P/COPERNICUS/bit.sea


. ../profile.inc


OUTPUTDIR=

INPUTFILE=
MASKFILE=

VARIABLE=
COASTNESS=
BASIN=
STATISTIC=


my_prex_or_die "python pkl_reader.py -o $OUTPUTDIR -i $INPUTFILE -m $MASKFILE " #-v $VARIABLE -c $COASTNESS -b $BASIN -s $STATISTIC "


