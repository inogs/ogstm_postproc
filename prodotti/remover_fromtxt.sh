#! /bin/bash

OUTDIR=$PWD/out

mkdir -p $OUTDIR

DATASETS="
cmems_mod_med_bgc-bio_anfc_4.2km_P1D-m
cmems_mod_med_bgc-car_anfc_4.2km_P1D-m
cmems_mod_med_bgc-nut_anfc_4.2km_P1D-m
cmems_mod_med_bgc-pft_anfc_4.2km_P1D-m
cmems_mod_med_bgc-co2_anfc_4.2km_P1D-m
cmems_mod_med_bgc-optics_anfc_4.2km_P1D-m
"
# DATASETS="
# med-ogs-bio-rean-d
# "

JUNKFILE=junk.txt
PARAMS="s3 ls --endpoint-url https://s3.waw3-1.cloudferro.com --no-sign-request"
for dataset in $DATASETS ; do  

   filename=$PWD/${dataset}.txt
   #VERSION=202211
   echo n | copernicusmarine get -i $dataset --filter "*/202509*d-OGS*" --create-file-list $JUNKFILE ; grep sm $JUNKFILE | grep sm $JUNKFILE > $filename
   rm $JUNKFILE
   #aws $PARAMS s3://mdl-native-12/native/MEDSEA_ANALYSISFORECAST_BGC_006_014/${dataset}_${VERSION}/2025/09/ | awk '{print $4}' | grep sm | grep -v 20250922_d- > $filename
   python3 remover_fromtxt.py -i $filename -o $OUTDIR --nomenclature new
done
