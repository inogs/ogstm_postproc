#! /bin/bash


usage() {
echo "Returns the name of a bucket of MDS Data Lake"
echo "SYNOPSIS"
echo "get_bucket.sh  [ -p PRODUCT_ID ] "
echo "EXAMPLE"
echo "get_bucket.sh -p MEDSEA_ANALYSISFORECAST_BGC_006_014"
echo ""
}

if [ $# -lt 2 ] ; then
  usage
  exit 1
fi


case $1 in
   "-p" )  PRODUCT_ID=$2;;
     *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
esac
shift 2


./ls_products.sh | grep $PRODUCT_ID | head -1 | cut -d \" -f 4
