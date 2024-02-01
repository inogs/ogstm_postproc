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


for dataset in $DATASETS ; do  

   filename=$PWD/${dataset}.txt
   echo n | copernicusmarine get -i $dataset --filter "*202312*d-OGS*" --show-outputnames | grep fc-sv08 | grep INFO > $filename 
   python remover_fromtxt.py -i $filename -o $OUTDIR

done