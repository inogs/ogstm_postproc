#! /bin/bash

PATH=$PATH:/gpfs/work/OGS20_PRACE_P/COPERNICUS/bin/

for month in 01 02 ; do
   for type in BIOL CARB NUTR PFTC CO2F ; do
    ./DNT_remove_generator.sh -t $type -y 2018 -m $month
    done
done 
