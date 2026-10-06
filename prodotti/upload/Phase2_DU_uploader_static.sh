#!/bin/bash

########  Phase2_DU_uploader_static.sh  ############
#   Sends products to COPERNICUS phase II DU       #
#      generates delivery note xml file            #
#                                                  #
#   Author: GB, 2026.10.06                         # 
####################################################


usage() {
echo "Uploads Static NRT product files"
echo "SYNOPSYS"
echo "Phase2_DU_uploader_static.sh [ -i PRODUCTDIR] [ -l LOGDIR ]"
echo ""
}

if [ $# -lt 4 ] ; then
  usage
  exit 1
fi

for I in 1 2 ; do
   case $1 in
      "-i" ) PROD_DIR=$2;;
      "-l" ) logDir=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done


BINDIR=/g100_work/OGS23_PRACE_IT/COPERNICUS/bin/
FILES_TO_SEND="MED_MFC_006_014_mask_bathy.nc MED_MFC_006_014_coordinates.nc"

dataset=cmems_mod_med_bgc_anfc_4.2km_static_202611



PushingEntity="MED-OGS-TRIESTE-IT"

###CONFIGURE THE LINES BELOW
product=MEDSEA_ANALYSISFORECAST_BGC_006_014
username=cmems_med_ogs
password=9J2e+uLU
host=ftp-nrt.marine.copernicus.eu
port=21
###



DntTime=`date --utc +%Y%m%dT%H%M%SZ`
DNT_FILE=${logDir}/${product}_${DntTime}.xml

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >  $DNT_FILE
echo "<delivery product=\"${product}\" PushingEntity=\"${PushingEntity}\" date=\"${DntTime}\">" >> $DNT_FILE
echo "    <dataset DatasetName=\"${dataset}\">" >> $DNT_FILE



for basefile in ${FILES_TO_SEND} ; do
    remotedir=/${product}/${dataset}
    remotefile="${basefile}"
    md5s=`md5sum ${PROD_DIR}/${basefile}|awk '{print $1}'`
	StarTime=`date --utc +%Y%m%dT%H%M%SZ`
	EndTime=${StarTime}
	NumberOfAttempts=1
	errCod=0

	TOTAL_RESEND_STR= 
   
	for i in `seq 1 10`;do

                  stderr=$( $BINDIR/ncftpput -P $port -u $username -p $password -T .tmp. $host $remotedir ${PROD_DIR}/${basefile} 2>&1 )
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
