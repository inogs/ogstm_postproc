#! /bin/bash

PROD_DIR=/pico/scratch/userexternal/gbolzon0/eas_v12/eas_v20_1/wrkdir/POSTPROC/output/PROD/UNZIPPED_ALL/

YEAR=2015
for type in BIOL CARB NUTR PFTC ; do
    ./Phase2_DU_uploader_dataset_006_014.sh -i $PROD_DIR -t $type -y $YEAR
done
