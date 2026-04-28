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
echo "Returns the name of a product in MDS"
echo "type can be: BIOL, CARB, NUTR, PFTC, CO2F, EXCO"
echo ""
echo "SYNOPSYS"
echo "get_monthly_product_in_DU.sh [ -d date ] [ -t type ]   "
echo "EXAMPLE"
echo "get_monthly_products_in_DU.sh -d 20250201 -t BIOL "
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



PRODUCT=MEDSEA_ANALYSISFORECAST_BGC_006_014



case $TYPE in 
   "BIOL" ) dataset=cmems_mod_med_bgc-bio_anfc_4.2km_P1M-m_202511 ;;
   "CARB" ) dataset=cmems_mod_med_bgc-car_anfc_4.2km_P1M-m_202511 ;;
   "NUTR" ) dataset=cmems_mod_med_bgc-nut_anfc_4.2km_P1M-m_202511 ;;
   "PFTC" ) dataset=cmems_mod_med_bgc-pft_anfc_4.2km_P1M-m_202511 ;;
   "CO2F" ) dataset=cmems_mod_med_bgc-co2_anfc_4.2km_P1M-m_202511 ;;
   "EXCO" ) dataset=cmems_mod_med_bgc-optics_anfc_4.2km_P1M-m_202511 ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac   

YYYY=${MONTH:0:4}
aws s3 ls --endpoint-url https://s3.waw3-1.cloudferro.com --no-sign-request s3://mdl-native-12/native/MEDSEA_ANALYSISFORECAST_BGC_006_014/${dataset}/${YYYY}/ | grep ${MONTH}_m-OGS | awk '{print $4}'





