#! /bin/bash

INPUTDIR=/g100_scratch/userexternal/gbolzon0/products/AVE
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/products/PRODUCTS
MASKFILE=/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.20190101*N1p.nc | cut -c 5-12 > $HERE/timelist

cd $HERE

mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20190115 --tr monthly --bulltype interim


BASEDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/
INPUTDIR=$BASEDIR/AVE_FREQ_1/
OUTPUTDIR=/gpfs/scratch/userexternal/gcoidess/PRODOTTI/daily/ 
MASKFILE=$BASEDIR/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.199901*N1p.nc | cut -c 5-12 > $HERE/timelist


mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20210323 --tr daily --bulltype analysis
