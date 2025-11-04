#!/bin/bash

##  Phase2_DU_uploader_dataset_006_014_monthly.sh ##
#   Sends products to COPERNICUS phase II DU       #
#      generates delivery note xml file            #
#                                                  #
#   Author: GB. 2018.02.09                         #
####################################################


usage() {
echo "Uploads chain product files"
echo "SYNOPSYS"
echo "Phase2_DU_uploader_dataset_006_014_monthly.sh [ -i PRODUCTDIR] [ -t TYPE ] [ -y $YEAR ] [ -l LOGDIR ]"
echo ""
}

if [ $# -lt 8 ] ; then
  usage
  exit 1
fi

for I in 1 2 3 4 ; do
   case $1 in
      "-i" ) PROD_DIR=$2;;
      "-t" ) TYPE=$2;;
      "-y" ) YEAR=$2;;
      "-l" ) logDir=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done

function decide_action {
   # arg1 = local product file
   # arg2 = remote product file
   # returns in the exit_status a code for the actions to do

   # 1 means nothing to do
   # 2 means send
   # 3 means send and delete
   # 4 means error

   local_file=$1
   remotefile=$2

   remotebul_time=${remotefile:34:8}
   local_bul_time=${local_file:34:8}
   local_type=${local_file:43:2}
   
   if [[ $local_type == fc ]] || [[ $local_type == sm ]]  ; then return 4 ; fi
   if [[ $remotefile == $local_file ]]   ; then return 1 ; fi
   if [[ $remotefile == "" ]]            ; then return 2 ; fi

   
   if [[ $local_bul_time > $remotebul_time ]]   ; then return 3 ; fi
   if [[ $local_bul_time < $remotebul_time ]]   ; then return 4 ; fi

}


BINDIR=/g100_work/OGS23_PRACE_IT/COPERNICUS/bin/
FILES_TO_SEND="${YEAR}*${TYPE}*.nc"


case $TYPE in
   "BIOL" ) dataset=cmems_mod_med_bgc-bio_anfc_4.2km_P1M-m_202511 ;;
   "CARB" ) dataset=cmems_mod_med_bgc-car_anfc_4.2km_P1M-m_202511 ;;
   "NUTR" ) dataset=cmems_mod_med_bgc-nut_anfc_4.2km_P1M-m_202511 ;;
   "PFTC" ) dataset=cmems_mod_med_bgc-pft_anfc_4.2km_P1M-m_202511 ;;
   "CO2F" ) dataset=cmems_mod_med_bgc-co2_anfc_4.2km_P1M-m_202511 ;;
   "EXCO" ) dataset=cmems_mod_med_bgc-optics_anfc_4.2km_P1M-m_202511 ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac


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

upload_xml=False

for file in `ls ${PROD_DIR}/${FILES_TO_SEND} ` ; do
    basefile=`basename $file `
    yyyy=${basefile:0:4}
      mm=${basefile:4:2}

    # -------------------------------------
    remote_name=`./get_monthly_product_in_DU.sh -d ${yyyy}${mm} -t $TYPE `
    decide_action $basefile $remote_name
    ACTION=$?
    # -------------------------------------
 case $ACTION in
   1) echo "$basefile already in DU" ;;
   2|3) echo "$basefile has to be sent"
    if [ $ACTION -eq 3 ]; then echo " and $remote_name will be removed "; fi
    remotedir=/${product}/${dataset}/$yyyy
    remotefile="${yyyy}/${basefile}"
    md5s=`md5sum $file|awk '{print $1}'`
	StarTime=`date --utc +%Y%m%dT%H%M%SZ`
	EndTime=${StarTime}
	NumberOfAttempts=1
	errCod=0

    to_remove_file=$yyyy/$remote_name
	DELETE_STR="<file FileName=\"${to_remove_file}\" > <KeyWord>Delete</KeyWord> </file>"

   
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
     if [ $status == Delivered ] && [ $ACTION -eq 3 ] ; then
        echo "             $DELETE_STR"  >> $DNT_FILE
    fi
	
	
	if [ ${NumberOfAttempts} -ne 1 ]; then
	  close=""
	  RESEND_STR="<resendAttempt DueToErrorCode=\"${lastErrCod}\" DueToErrorMsg=\"${lastError}\" NumberOfAttempts=\"${NumberOfAttempts}\"/>"
	  echo "                         $RESEND_STR" >> $DNT_FILE
	  echo "                </file>" >> $DNT_FILE
	fi
    ;;

   4) echo "ERROR in send algorithm "
      echo "You are trying to replace: a product with a lower quality one"
      ;;
   *) echo "wrong decide_action exit status"; exit 1 ;;
 esac

done

echo "    </dataset>"  >> $DNT_FILE
echo "</delivery>" >> $DNT_FILE

if [ $upload_xml == "True" ] ; then
   echo "Now uploading $DNT_FILE"
else
   echo "$DNT_FILE can be manually uploaded to MDS"
fi
