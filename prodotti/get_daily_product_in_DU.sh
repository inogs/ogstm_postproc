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
echo "type can be: BIOL, CARB, NUTR, PFTC, CO2F EXCO"
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

HOST=nrt.cmems-du.eu
ncftp -P 21 -u MED_OGS_TRIESTE_IT -p NEdifupa $HOST <<EOF
dir $filename
EOF

}

PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014

case $TYPE in 
   "BIOL" ) dataset=cmems_mod_med_bgc-bio_anfc_4.2km_P1D-m ;;
   "CARB" ) dataset=cmems_mod_med_bgc-car_anfc_4.2km_P1D-m ;;
   "NUTR" ) dataset=cmems_mod_med_bgc-nut_anfc_4.2km_P1D-m ;;
   "PFTC" ) dataset=cmems_mod_med_bgc-pft_anfc_4.2km_P1D-m ;;
   "CO2F" ) dataset=cmems_mod_med_bgc-co2_anfc_4.2km_P1D-m ;;
   "EXCO" ) dataset=cmems_mod_med_bgc-optics_anfc_4.2km_P1D-m ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac   


     yyyy=${DAY:0:4}
       mm=${DAY:4:2}
     remotepath=/Core/${PRODUCT}/${dataset}/${yyyy}/${mm}/${DAY}*
     ncftp_check $remotepath | grep MED | awk '{ print $9}'
     



