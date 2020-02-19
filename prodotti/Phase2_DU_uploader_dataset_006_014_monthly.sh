#!/bin/bash

####     DNT_generator_dataset.sh  #           #####
#   Sends products to COPERNICUS phase II DU       #
#      generates delivery note xml file            #
#                                                  #
#   Author: GB. 2018.02.09                         #
####################################################


usage() {
echo "Uploads chain product files"
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


BINDIR=/gpfs/work/OGS18_PRACE_P_0/COPERNICUS/bin/

ARCHIVE_DIR=/marconi/home/usera07ogs/a07ogs00/OPA/V3C/archive/
#
RUNDATE=20180313

FILES_TO_SEND="${YEAR}*${type}*.nc"

if [[ "$type" == "BIOL" ]]; then
   dataset=med00-ogs-bio-an-fc-m_202003
fi
if [[ "$type" == "CARB" ]]; then
   dataset=med00-ogs-car-an-fc-m_202003
fi
if [[ "$type" == "NUTR" ]]; then
   dataset=med00-ogs-nut-an-fc-m_202003
fi
if [[ "$type" == "PFTC" ]]; then
   dataset=med00-ogs-pft-an-fc-m_202003
fi
if [[ "$type" == "CO2F" ]]; then
   dataset=med00-ogs-co2-an-fc-m_202003
fi


PushingEntity="MED-OGS-TRIESTE-IT"

###CONFIGURE THE LINES BELOW
product=MEDSEA_ANALYSIS_FORECAST_BIO_006_014
username=cmems_med_ogs
password=9J2e+uLU
host=nrt.cmems-du.eu
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
      mm=${basefile:4:2}
    remotedir=/${product}/${dataset}/$yyyy  #/$mm
    remotefile="${basefile}"
    md5s=`md5sum $file|awk '{print $1}'`
	StarTime=`date --utc +%Y%m%dT%H%M%SZ`
	EndTime=${StarTime}
	NumberOfAttempts=1
	errCod=0
	#to_remove_file=$( python rolling_archive.py -p $basefile -d $RUNDATE -g $type -a $ARCHIVE_DIR )
	#echo "python rolling_archive.py -p $basefile -d $RUNDATE -g $type -a $ARCHIVE_DIR"
	#if [ ${to_remove_file} != "None"  ] ; then
	#    DELETE_STR="<file FileName=\"${to_remove_file}\" > <KeyWord>Delete</KeyWord> </file>"
	#fi
	
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
#	if [ $status == Delivered ] && [ ${to_remove_file} != "None"  ] ; then 
#	    echo "             $DELETE_STR"  >> $DNT_FILE
#	fi
	
	
	if [ ${NumberOfAttempts} -ne 1 ]; then
	  close=""
	  RESEND_STR="<resendAttempt DueToErrorCode=\"${lastErrCod}\" DueToErrorMsg=\"${lastError}\" NumberOfAttempts=\"${NumberOfAttempts}\"/>"
	  echo "                         $RESEND_STR" >> $DNT_FILE
	  echo "                </file>" >> $DNT_FILE
	fi


done

echo "    </dataset>"  >> $DNT_FILE
echo "</delivery>" >> $DNT_FILE
