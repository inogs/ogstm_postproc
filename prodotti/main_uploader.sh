#! /bin/bash

PATH=$PATH:/gpfs/work/OGS18_PRACE_P_0/COPERNICUS/bin/
PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/bin_prod/prodotti/REAN_PRODS

YEAR=2015
for type in BIOL CARB NUTR PFTC; do
    ./Phase2_DU_uploader_dataset_006_008.sh -i $PROD_DIR -t $type -y $YEAR
done


exit 0




PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/MONTHLY/PROD

YEAR=2019
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_014_monthly.sh -i $PROD_DIR -t $type -y $YEAR
done


exit 0

PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/AVE_FREQ_1/PROD

YEAR=2019
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_014.sh -i $PROD_DIR -t $type -y $YEAR
done
