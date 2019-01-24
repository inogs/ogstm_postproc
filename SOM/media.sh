#! /bin/bash

export OPA_HOME=PERSEUS-BAU
DATADIR=/gss/gss_work/try14_bolzon/plazzari/${OPA_HOME}/wrkdir/MODEL
MLDDIR=/pico/home/userexternal/plazzari/SOM-MED/MLD
OUTPUT_DATA=/gss/gss_work/try14_bolzon/plazzari/${OPA_HOME}/wrkdir/SOM-ANALYSIS/DATA

for var in P1i P2i P3i P4i N1p N3n phys ppn;do
    for mm in  $(seq -f "%02g" 1 12); do
        ncea -O $DATADIR/ave.200?${mm}??-??:??:??.${var}.nc ave.${mm}.${var}.nc
    done
done

for mm in  $(seq -f "%02g" 1 12); do
    ncea -O $MLDDIR/ave.200?${mm}??-??:??:??.MLD.nc ave.${mm}.MLD.nc
done

for mm in $(seq -f "%02g" 1 12); do
    cp ave.${mm}.P1i.nc ave.${mm}.nc

    ncrename -d time_counter,time ave.${mm}.phys.nc
    ncrename -d x,lon ave.${mm}.phys.nc
    ncrename -d y,lat ave.${mm}.phys.nc
    ncrename -d deptht,depth ave.${mm}.phys.nc

    ncrename -d x,lon ave.${mm}.MLD.nc
    ncrename -d y,lat ave.${mm}.MLD.nc

    for var in P2i P3i P4i N1p N3n ppn MLD;do
        ncks -v ${var} -A ave.${mm}.${var}.nc ave.${mm}.nc
        rm -f ave.${mm}.${var}.nc
    done 
    ncks  -A ave.${mm}.phys.nc ave.${mm}.nc 
    rm -f ave.${mm}.phys.nc
done

rm ave.??.P1i.nc
mv ave.??.nc $OUTPUT_DATA
