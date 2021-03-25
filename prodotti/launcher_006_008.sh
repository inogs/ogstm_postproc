#! /bin/bash

#INPUTDIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/MODEL/AVE_FREQ_1
#OUTPUTDIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/MONTHLY/PROD
#MASKFILE=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/MODEL/meshmask.nc

#mkdir -p $OUTPUTDIR
#HERE=$PWD
#cd $INPUTDIR
#ls ave.20190101*N1p.nc | cut -c 5-12 > $HERE/timelist

#cd $HERE

#mpirun python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20190115 --tr monthly


BASEDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/
INPUTDIR=$BASEDIR/AVE_FREQ_1/
OUTPUTDIR=/gpfs/scratch/userexternal/gcoidess/PRODOTTI/daily/ 
MASKFILE=$BASEDIR/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.199901*N1p.nc | cut -c 5-12 > $HERE/timelist


mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20210323 --tr daily
