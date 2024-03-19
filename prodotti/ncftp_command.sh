#! /bin/bash

HOST=ftp-nrt-dta.marine.copernicus.eu
PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014

for YEAR in $(seq 2022 2027) ; do
	for group in bio car nut co2 optics pft; do
	    dataset=cmems_mod_med_bgc-${group}_anfc_4.2km_P1D-m_202211
	    if [ $group == 'pft' ] ; then
		   dataset=cmems_mod_med_bgc-${group}_anfc_4.2km_P1D-m_202311
            fi
	    /g100_work/OGS23_PRACE_IT/COPERNICUS/bin/ncftp -P 21 -u cmems_med_ogs -p 9J2e+uLU $HOST <<EOF
cd /${PRODUCT}/${dataset}
mkdir ${YEAR}
cd ${YEAR}
mkdir 01 02 03 04 05 06 07 08 09 10 11 12
quit
EOF

    done
done

