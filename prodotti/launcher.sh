#! /bin/bash

INPUTDIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/MODEL/AVE_FREQ_1
OUTPUTDIR=/gpfs/work/OGS18_PRACE_P_0/PROD_COPERNICUS/prodotti/MONTHLY
MASKFILE=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/MODEL/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave*N1p.nc | cut -c 5-21 > $HERE/timelist

cd $HERE
mpirun python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE

mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d sm -b 20190115 -tr daily
mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20190115 --tr monthly
