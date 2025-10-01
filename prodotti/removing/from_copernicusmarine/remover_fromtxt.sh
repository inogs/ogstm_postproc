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

for dataset in $DATASETS ; do  

   filename=$PWD/${dataset}.txt

   echo n | copernicusmarine get -i $dataset --filter "*/202509*d-OGS*" --create-file-list $JUNKFILE ; grep sm $JUNKFILE | grep sm $JUNKFILE > $filename
   rm $JUNKFILE
   python3 remover_fromtxt.py -i $filename -o $OUTDIR --nomenclature new
   sleep 1 # be sure not do overwrite the xml
done
