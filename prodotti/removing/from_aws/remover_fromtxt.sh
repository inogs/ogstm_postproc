#! /bin/bash

OUTDIR=$PWD/out

mkdir -p $OUTDIR
PRODUCT_ID=MEDSEA_ANALYSISFORECAST_BGC_006_014

DATASETS="
cmems_mod_med_bgc-bio_anfc_4.2km_P1M-m
cmems_mod_med_bgc-car_anfc_4.2km_P1M-m
cmems_mod_med_bgc-nut_anfc_4.2km_P1M-m
cmems_mod_med_bgc-pft_anfc_4.2km_P1M-m
cmems_mod_med_bgc-co2_anfc_4.2km_P1M-m
cmems_mod_med_bgc-optics_anfc_4.2km_P1M-m
"
# DATASETS="
# med-ogs-bio-rean-d
# "

JUNKFILE=junk.txt
PARAMS="s3 ls --endpoint-url https://s3.waw3-1.cloudferro.com --no-sign-request"
for dataset in $DATASETS ; do  

   filename=$PWD/${dataset}.txt
   VERSION=202511

   aws $PARAMS s3://mdl-native-12/native/${PRODUCT_ID}/${dataset}_${VERSION}/2025/  | awk '{print $4}' |grep  20250927_m- > $filename
   python3 remover_fromtxt.py -i $filename -o $OUTDIR -p $PRODUCT_ID -d $dataset -v $VERSION
   sleep 1 # be sure not do overwrite the xml
done
