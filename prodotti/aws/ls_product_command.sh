#! /bin/bash


usage() {
echo "Returns the aws command line to get ls of a product"
echo "Useful to navigate MDS"
echo "SYNOPSIS"
echo "ls_product_command.sh  [ -p PRODUCT_ID ] "
echo "EXAMPLE"
echo "ls_product_command.sh -p MEDSEA_ANALYSISFORECAST_BGC_006_014"
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

BKT=$(./get_bucket.sh -p $PRODUCT_ID)

echo aws s3 ls --endpoint-url https://s3.waw3-1.cloudferro.com --no-sign-request s3://${BKT}/native/${PRODUCT_ID}/