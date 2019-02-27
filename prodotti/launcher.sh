#! /bin/bash

INPUTDIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/MODEL/AVE_FREQ_1
OUTPUTDIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/AVE_FREQ_1/PROD
MASKFILE=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/MODEL/meshmask.nc

#INPUTDIR=/gpfs/scratch/userexternal/gbolzon0/REA/2017
#OUTPUTDIR=/gpfs/work/OGS18_PRACE_P_0/PROD_COPERNICUS/prodotti/REAN/
#MASKFILE=/gpfs/scratch/userexternal/gbolzon0/REA/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.20190101*N1p.nc | cut -c 5-12 > $HERE/timelist

cd $HERE
#mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist2 -m $MASKFILE

mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d sm -b 20190115 --tr daily

exit 0

mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20190115 --tr monthly
