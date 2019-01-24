#! /bin/bash

HOST=nrt.cmems-du.eu
PRODUCT=MEDSEA_ANALYSIS_FORECAST_BIO_006_014

for YEAR in $(seq 2015 2018 ) ; do 
	for group in bio car nut pft ; do
	    dataset=sv03-med-ogs-${group}-an-fc-d
		/marconi/home/usera07ogs/a07ogs00/OPA/V3C/HOST/marconi/bin/ncftp -P 21 -u cmems_med_ogs -p 9J2e+uLU $HOST <<EOF
cd /${PRODUCT}/${dataset}
mkdir ${YEAR}
cd ${YEAR}
mkdir 01 02 03 04 05 06 07 08 09 10 11 12
quit
EOF

    done
done
