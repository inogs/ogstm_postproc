#! /bin/bash

PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/AVE_FREQ_1/PROD

YEAR=2019
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_014.sh -i $PROD_DIR -t $type -y $YEAR
done
