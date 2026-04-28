#! /bin/bash


export PATH=$PATH:/leonardo_work/OGS_prod2528_0/OPA/V11C-dev/HOST/leonardo/bin/


YEAR=2025
logDir=./XML_monthly
mkdir -p $logDir

PROD_DIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/MONTHLY/RE
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_008_monthly.sh -i $PROD_DIR -t $type -y $YEAR -l $logDir
done

PROD_DIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/MONTHLY/IN
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_008_monthly.sh -i $PROD_DIR -t $type -y $YEAR -l $logDir
done


YEAR=2025
logDir=./XML_daily
mkdir -p $logDir

PROD_DIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/DAILY/RE
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_008_daily.sh -i $PROD_DIR -t $type -y $YEAR -l $logDir
done

PROD_DIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/DAILY/IN
for type in BIOL CARB NUTR PFTC CO2F; do
    ./Phase2_DU_uploader_dataset_006_008_daily.sh -i $PROD_DIR -t $type -y $YEAR -l $logDir
done

exit 0



PROD_DIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/YEARLY/
logDir=./XML
mkdir -p $logDir

for type in BIOL CARB NUTR PFTC CO2F; do
#    ./Phase2_DU_uploader_dataset_006_008_yearly.sh -i $PROD_DIR -t $type -l $logDir
done


PROD_DIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/CLIM
./Phase2_DU_uploader_dataset_006_008_clim.sh -i $PROD_DIR -l $logDir

