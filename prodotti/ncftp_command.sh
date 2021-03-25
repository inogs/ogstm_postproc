#! /bin/bash

HOST=my.cmems-du.eu
PRODUCT=MEDSEA_MULTIYEAR_BGC_006_008

for YEAR in $(seq 1999 2022) ; do
	for group in bio car nut pft co2 ; do
            dataset=med-ogs-${group}-rean-d_202105
	    /gpfs/work/OGS20_PRACE_P/COPERNICUS/bin/ncftp -P 21 -u cmems_med_ogs -p 9J2e+uLU $HOST <<EOF
cd /${PRODUCT}/${dataset}
mkdir ${YEAR}
cd ${YEAR}
mkdir 01 02 03 04 05 06 07 08 09 10 11 12
quit
EOF

    done
done
