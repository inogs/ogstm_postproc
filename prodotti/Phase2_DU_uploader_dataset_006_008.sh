#!/bin/bash

####     DNT_generator_dataset.sh  #           #####
#   Sends products to COPERNICUS phase II DU       #
#      generates delivery note xml file            #
#                                                  #
#   Author: GB. 2018.02.09                         #
####################################################


usage() {
echo "Uploads Reanalysis product files"
echo "SYNOPSYS"
echo "DNT_generator_dataset.sh [ -i PRODUCTDIR] [ -t TYPE ] [ -y $YEAR ]"
echo ""
}

if [ $# -lt 6 ] ; then
  usage
  exit 1
fi

for I in 1 2 3 ; do
   case $1 in
      "-i" ) PROD_DIR=$2;;
      "-t" ) type=$2;;
      "-y" ) YEAR=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done


BINDIR=/marconi/home/usera07ogs/a07ogs00/OPA/V3C/HOST/marconi/bin



FILES_TO_SEND="${YEAR}*${type}*.nc"

if [[ "$type" == "BIOL" ]]; then
   dataset=sv03-med-ogs-bio-rean-m
fi
if [[ "$type" == "CARB" ]]; then
   dataset=sv03-med-ogs-car-rean-m
fi
if [[ "$type" == "NUTR" ]]; then
   dataset=sv03-med-ogs-nut-rean-m
fi
if [[ "$type" == "PFTC" ]]; then
   dataset=sv03-med-ogs-pft-rean-m
fi


PushingEntity="MED-OGS-TRIESTE-IT"

###CONFIGURE THE LINES BELOW
product=MEDSEA_REANALYSIS_BIO_006_008
username=cmems_med_ogs
password=9J2e+uLU
host=my.cmems-du.eu
logDir=. #log
port=21
###



DntTime=`date --utc +%Y%m%dT%H%M%SZ`
DNT_FILE=${logDir}/${product}_${DntTime}.xml

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >  $DNT_FILE
echo "<delivery product=\"${product}\" PushingEntity=\"${PushingEntity}\" date=\"${DntTime}\">" >> $DNT_FILE
echo "    <dataset DatasetName=\"${dataset}\">" >> $DNT_FILE


for file in `ls ${PROD_DIR}/${FILES_TO_SEND} ` ; do
    basefile=`basename $file `
    yyyy=${basefile:0:4}
    remotedir=/${product}/${dataset}/$yyyy
    remotefile="${yyyy}/${basefile}"
    md5s=`md5sum $file|awk '{print $1}'`
	StarTime=`date --utc +%Y%m%dT%H%M%SZ`
	EndTime=${StarTime}
	NumberOfAttempts=1
	errCod=0
	
	TOTAL_RESEND_STR= 
   
	for i in `seq 1 10`;do

   		  stderr=$( $BINDIR/ncftpput -P $port -u $username -p $password -T .tmp. $host $remotedir ${file} 2>&1 >/dev/tty )
		  errCod=$?

		  if [ ${errCod} -eq 0 ];then
		      EndTime=`date --utc +%Y%m%dT%H%M%SZ`
		      break
		  else
		      # storage on arrays for future use  ##########
              ERRCOD[$NumberOfAttempts]=${errCod}
              STDERR[$NumberOfAttempts]=${stderr}
              ##############################################
		      lastErrCod=${errCod}
		      lastError=${stderr}
		      ((NumberOfAttempts++))
		    
		  fi
	done
	status=Delivered
	if [ "${StarTime}" == "${EndTime}" ];then
	  status=Failed
	  if [ $NumberOfAttempts -eq 11 ] ; then
	     NumberOfAttempts=10
	  fi
	fi
	
	if [ ${NumberOfAttempts} -eq 1 ] ; then 
	    close="/"
	else
	    close=""
	fi
	FINAL_STR="<file FileName=\"${remotefile}\" StartUploadTime=\"${StarTime}\"  StopUploadTime=\"${EndTime}\" Checksum=\"${md5s}\"  FinalStatus=\"${status}\"${close}>"
	echo "             $FINAL_STR" >> $DNT_FILE

	
	if [ ${NumberOfAttempts} -ne 1 ]; then
	  close=""
	  RESEND_STR="<resendAttempt DueToErrorCode=\"${lastErrCod}\" DueToErrorMsg=\"${lastError}\" NumberOfAttempts=\"${NumberOfAttempts}\"/>"
	  echo "                         $RESEND_STR" >> $DNT_FILE
	  echo "                </file>" >> $DNT_FILE
	fi


done

echo "    </dataset>"  >> $DNT_FILE
echo "</delivery>" >> $DNT_FILE
