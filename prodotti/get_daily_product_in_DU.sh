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
echo "check_daily_products_in_DU.sh -d 20190206 -t BIOL "
echo ""
}

if [ $# -lt 4 ] ; then
  usage
  exit 1
fi

for I in 1 2; do
   case $1 in
      "-d" )  DAY=$2;;
      "-t" )  TYPE=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done

function ncftp_check {
filename=$1

HOST=nrt-dev.cmems-du.eu
ncftp -P 21 -u MED_OGS_TRIESTE_IT -p NEdifupa $HOST <<EOF
dir $filename
EOF

}

PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014

case $TYPE in 
   "BIOL" ) dataset=med-ogs-bio-an-fc-d ;;
   "CARB" ) dataset=med-ogs-car-an-fc-d ;;
   "NUTR" ) dataset=med-ogs-nut-an-fc-d ;;
   "PFTC" ) dataset=med-ogs-pft-an-fc-d ;;
   "CO2F" ) dataset=med-ogs-co2-an-fc-d ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac   


     yyyy=${DAY:0:4}
       mm=${DAY:4:2}
     remotepath=/Core/${PRODUCT}/${dataset}/${yyyy}/${mm}/${DAY}*
     ncftp_check $remotepath | grep MED | awk '{ print $9}'
     



