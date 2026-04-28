#! /bin/bash

INPUTDIR=/g100_work/OGS_prodC/OPA/V10C-prod/archive/analysis/20241001/POSTPROC/AVE_FREQ_1/ARCHIVE/
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/V11C/test_upload/DAILY
MASKFILE=/g100_work/OGS_prodC/OPA/V10C-prod/etc/static-data/MED24_125/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.*N1p.nc | cut -c 5-12 > $HERE/timelist

cd $HERE


mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20241008 --tr daily

### monthly section

INPUTDIR=/g100_scratch/userexternal/gbolzon0/V11C/test_upload/ogstm_postproc/prodotti/MONTHLY
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/V11C/test_upload/MONTHLY
mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.*N1p.nc | cut -c 5-12 > $HERE/timelist

cd $HERE

mpirun -np 1 python prodotti_copernicus.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -d an -b 20241008 --tr monthly
