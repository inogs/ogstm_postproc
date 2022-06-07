#! /bin/bash

INPUTDIR=/g100_scratch/userexternal/gbolzon0/V9C/PRODOTTI/AVE_CLIM
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/V9C/PRODOTTI/
MASKFILE=/gss/gss_work/DRES_OGS_BiGe/ateruzzi/RA_24/input/setup/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc


python prodotti_copernicus_rea_clim.py -i $INPUTDIR -o $OUTPUTDIR -m $MASKFILE -b 20220607 --bulltype analysis



INPUTDIR=/g100_scratch/userexternal/gbolzon0/V9C/PRODOTTI/AVE_YEARLY
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/V9C/PRODOTTI/YEARLY

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.*N1p.nc | cut -c 5-12 > $HERE/timelist

cd $HERE

mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20110607 --tr yearly --bulltype analysis


BASEDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/
INPUTDIR=$BASEDIR/AVE_FREQ_1/
OUTPUTDIR=/gpfs/scratch/userexternal/gcoidess/PRODOTTI/daily/ 
MASKFILE=$BASEDIR/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.199901*N1p.nc | cut -c 5-12 > $HERE/timelist


mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20210323 --tr daily --bulltype analysis
