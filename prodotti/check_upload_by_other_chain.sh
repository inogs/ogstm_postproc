#! /bin/bash

###################################################
#
#        check_upload_by_other_chain.sh
#
#  Looks for DNT response data to check if
#    upload once again product files  
#
#   Author: Giorgio Bolzon
##################################################

usage() {
echo "Looks for DNT response data to check if the other chain has already uploaded product files"
echo "Returned value is in exit status"
echo "Exit status  0 means ok, files are already uploaded"
echo "Exit status 10 means no files, upload is needed"
echo ""
echo "SYNOPSYS"
echo "check_upload_by_other_chain.sh [ -d RUNDATE] [-l localdir ] [ -f config ] "
echo "EXAMPLE"
echo "check_upload_by_other_chain.sh -d 20180411  -l mydir -f config.du"
echo ""
}

if [ $# -lt 6 ] ; then
  usage
  exit 1
fi

for I in 1 2 3; do
   case $1 in
      "-d" ) RUNDATE=$2;;
      "-l" ) LOCALDIR=$2;;
      "-f" ) CONFIGFILE=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done


product=MEDSEA_ANALYSIS_FORECAST_BIO_006_014

REMOTEDIR=${product}/DNT_response

# ! work on fresh local dir
rm -rf $LOCALDIR
mkdir -p $LOCALDIR


RESPONSE_FILES="${product}_${RUNDATE}*response.xml"

ncftpget -f $CONFIGFILE $LOCALDIR ${REMOTEDIR}/${RESPONSE_FILES} 

COUNT=$( ls $LOCALDIR | wc -l ) # expected value: 4

TO_UPLOAD=false

if [ $COUNT -lt 4 ] ; then
   echo "Number of files < 4, upload needed"
   exit 10
else
   for I in $( ls $LOCALDIR/*xml ) ; do
       RES=$( python response_reader.py -i $I )
       [[ $RES == "validated" ]] || exit 10
   done
fi

echo "TO UPLOAD = $TO_UPLOAD"