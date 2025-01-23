#!/bin/bash

### Phase2_DU_uploader_dataset_006_008_daily.sh  ###
#   Sends products to COPERNICUS phase II DU       #
#      generates delivery note xml file            #
#                                                  #
#   Author: GB. 2018.02.09                         # 
#   MOD : GC. 2021.03.25                           #
####################################################


usage() {
echo "Uploads Reanalysis product files"
echo "SYNOPSYS"
echo "Phase2_DU_uploader_dataset_006_008_daily.sh [ -i PRODUCTDIR] [ -t TYPE ] [ -y YEAR ] [ -l LOGDIR ]"
echo ""
}

if [ $# -lt 8 ] ; then
  usage
  exit 1
fi

for I in 1 2 3 4; do
   case $1 in
      "-i" ) PROD_DIR=$2;;
      "-t" ) type=$2;;
      "-y" ) YEAR=$2;;
      "-l" ) logDir=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done


BINDIR=/g100_work/OGS23_PRACE_IT/COPERNICUS/bin


FILES_TO_SEND="${YEAR}*${type}*.nc"

if [[ "$type" == "BIOL" ]]; then
   dataset=med-ogs-bio-rean-d_202105
fi
if [[ "$type" == "CARB" ]]; then
   dataset=med-ogs-car-rean-d_202105
fi
if [[ "$type" == "CO2F" ]]; then
   dataset=med-ogs-co2-rean-d_202105
fi
if [[ "$type" == "NUTR" ]]; then
   dataset=med-ogs-nut-rean-d_202105
fi
if [[ "$type" == "PFTC" ]]; then
   dataset=med-ogs-pft-rean-d_202105
fi


PushingEntity="MED-OGS-TRIESTE-IT"

###CONFIGURE THE LINES BELOW
product=MEDSEA_MULTIYEAR_BGC_006_008
username=cmems_med_ogs
password=9J2e+uLU
host=ftp-my.marine.copernicus.eu
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
    mm=${basefile:4:2}
    remotedir=/${product}/${dataset}/$yyyy/$mm
    remotefile="${yyyy}/${mm}/${basefile}"
    md5s=`md5sum $file|awk '{print $1}'`
	StarTime=`date --utc +%Y%m%dT%H%M%SZ`
	EndTime=${StarTime}
	NumberOfAttempts=1
	errCod=0
	
	TOTAL_RESEND_STR= 
   
	for i in `seq 1 10`;do
		  stderr=$( $BINDIR/ncftpput -P $port -u $username -p $password -T .tmp. $host $remotedir ${file} 2>&1 )
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
