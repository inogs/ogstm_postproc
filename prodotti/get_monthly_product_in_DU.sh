#! /bin/bash

###################################################
#
#          get_daily_products_in_DU.sh
#
#        Looks for a product file in DU
#
#          Author: Giorgio Bolzon
##################################################

usage() {
echo "Returns the name of a product in DU phase 2 production position"
echo "Needs in PATH the path of ncftp "
echo "type can be: BIOL, CARB, NUTR, PFTC, CO2F"
echo ""
echo "SYNOPSYS"
echo "get_daily_product_in_DU.sh [ -d date ] [ -t type ]   "
echo "EXAMPLE"
echo "check_monthly_products_in_DU.sh -d 20190201 -t BIOL "
echo ""
}

if [ $# -lt 4 ] ; then
  usage
  exit 1
fi

for I in 1 2; do
   case $1 in
      "-d" )  MONTH=$2;;
      "-t" )  TYPE=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done

function ncftp_check {
filename=$1

HOST=nrt.cmems-du.eu
ncftp -P 21 -u MED_OGS_TRIESTE_IT -p NEdifupa $HOST <<EOF
dir $filename
EOF

}

PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014

case $TYPE in 
   "BIOL" ) dataset=med-ogs-bio-an-fc-m ;;
   "CARB" ) dataset=med-ogs-car-an-fc-m ;;
   "NUTR" ) dataset=med-ogs-nut-an-fc-m ;;
   "PFTC" ) dataset=med-ogs-pft-an-fc-m ;;
   "CO2F" ) dataset=med-ogs-co2-an-fc-m ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac   


     yyyy=${MONTH:0:4}
     remotepath=/Core/${PRODUCT}/${dataset}/${yyyy}/${MONTH}*
     ncftp_check $remotepath | grep MED | awk '{ print $9}'
     



