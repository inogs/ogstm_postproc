#! /bin/bash


PROD_DIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/YEARLY/
logDir=./XML
mkdir -p $logDir

for type in BIOL CARB NUTR PFTC CO2F; do
#    ./Phase2_DU_uploader_dataset_006_008_yearly.sh -i $PROD_DIR -t $type -l $logDir
done


PROD_DIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/CLIM
./Phase2_DU_uploader_dataset_006_008_clim.sh -i $PROD_DIR -l $logDir

exit 0

PROD_DIR=/gpfs/scratch/userexternal/gcoidess/PRODOTTI/daily/

YEAR=1999
logDir=./XML
mkdir -p $logDir

for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_008_daily.sh -i $PROD_DIR -t $type -y $YEAR -l $logDir
done


exit 0




PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/MONTHLY/PROD

YEAR=2019
for type in BIOL CARB NUTR PFTC CO2F EXCO; do
    ./Phase2_DU_uploader_dataset_006_014_monthly.sh -i $PROD_DIR -t $type -y $YEAR
done


exit 0

PROD_DIR=/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_07/wrkdir/POSTPROC/output/AVE_FREQ_1/PROD

YEAR=2019
for type in BIOL CARB NUTR PFTC CO2F EXCO; do
    ./Phase2_DU_uploader_dataset_006_014_daily.sh -i $PROD_DIR -t $type -y $YEAR
done
