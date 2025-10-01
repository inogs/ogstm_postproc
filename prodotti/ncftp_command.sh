#! /bin/bash
# Executed as the DV is opened by the CMEMS system to create the directory structure on the FTP server
# before an Entry In Service (here EIS 202511)

HOST=ftp-nrt.marine.copernicus.eu
PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014

# daily section

for YEAR in $(seq 2023 2029) ; do
	for group in bio car nut co2 optics pft; do
	    dataset=cmems_mod_med_bgc-${group}_anfc_4.2km_P1D-m_202511
	    ncftp -P 21 -u cmems_med_ogs -p 9J2e+uLU $HOST <<EOF
cd /${PRODUCT}/${dataset}
mkdir ${YEAR}
cd ${YEAR}
mkdir 01 02 03 04 05 06 07 08 09 10 11 12
quit
EOF

    done
done

# monthly section

for YEAR in $(seq 2023 2029) ; do
        for group in bio car nut co2 optics pft; do
            dataset=cmems_mod_med_bgc-${group}_anfc_4.2km_P1M-m_202511
            ncftp -P 21 -u cmems_med_ogs -p 9J2e+uLU $HOST <<EOF
cd /${PRODUCT}/${dataset}
mkdir ${YEAR}
quit
EOF

    done
done
