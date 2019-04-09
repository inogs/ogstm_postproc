#! /bin/bash

###################################################
#
#          check_monthly_products_in_DU.sh
#
#  Looks for product files in DU to check if
#    upload once again product files  
#
#   Author: Giorgio Bolzon
##################################################

usage() {
echo "Checks if the other chain has already uploaded product files"
echo "or if the monthly file has already been uploaded by itself, the previous run"

echo "For each dataset, it looks for last product file in DU phase 2 production position"
echo "Returned value is in exit status"
echo "Exit status  0 means ok, files are already uploaded"
echo "Exit status  1 means no files, upload is needed"
echo ""
echo "SYNOPSYS"
echo "check_monthly_products_in_DU.sh [ -p productdir ] [ -t tmpfile ] [-b -bindir]  "
echo "EXAMPLE"
echo "check_monthly_products_in_DU.sh -p /path/PROD/  -t tmp.txt -b bindir"
echo ""
}

if [ $# -lt 6 ] ; then
  usage
  exit 1
fi

for I in 1 2 3; do
   case $1 in
      "-p" ) PRODDIR=$2;;
      "-t" ) TMPFILE=$2;;
      "-b" )  BINDIR=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done

function ncftp_check {
filename=$1

HOST=nrt.cmems-du.eu
$BINDIR/ncftp -P 21 -u MED_OGS_TRIESTE_IT -p NEdifupa $HOST <<EOF
dir $filename
EOF

}

PRODUCT=MEDSEA_ANALYSIS_FORECAST_BIO_006_014

for type in BIOL CARB NUTR PFTC CO2F ; do
if [[ "$type" == "BIOL" ]]; then
   dataset=med-ogs-bio-an-fc-m_201904
fi
if [[ "$type" == "CARB" ]]; then
   dataset=med-ogs-car-an-fc-m_201904
fi
if [[ "$type" == "NUTR" ]]; then
   dataset=med-ogs-nut-an-fc-m_201904
fi
if [[ "$type" == "PFTC" ]]; then
   dataset=med-ogs-pft-an-fc-m_201904
fi
if [[ "$type" == "CO2F" ]]; then
   dataset=med-ogs-co2-an-fc-m_201904
fi


     lastfile_path=$( ls $PRODDIR/*${type}* | tail -1 )
     filename=`basename $lastfile_path`
     yyyy=${filename:0:4}
       mm=${filename:4:2}
      remotepath=/Core/${PRODUCT}/${dataset}/${yyyy}/${mm}/$filename
     ncftp_check $remotepath > $TMPFILE
     
     # grep also dumps in stdout, it is a check about DU publishing time
     grep $filename $TMPFILE  
     
     ANS=$?
     if [ $ANS -ne 0 ] ; then
       exit 1
     fi
done

