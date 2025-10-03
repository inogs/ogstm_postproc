#! /bin/bash

product=MEDSEA_ANALYSIS_FORECAST_BIO_006_014
logDir=.
DntTime=`date --utc +%Y%m%dT%H%M%SZ`
DNT_FILE=${logDir}/${product}_${DntTime}.xml

year=2018


echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"  >  $DNT_FILE
echo "<delivery product=\"${product}\" PushingEntity=\"${PushingEntity}\" date=\"${DntTime}\">" >> $DNT_FILE



for TYPE in BIOL CARB NUTR PFTC CO2F ; do

	case $TYPE in
	   "BIOL" ) dataset=med00-ogs-bio-an-fc-d_202003 ;;
	   "CARB" ) dataset=med00-ogs-car-an-fc-d_202003 ;;
	   "NUTR" ) dataset=med00-ogs-nut-an-fc-d_202003 ;;
	   "PFTC" ) dataset=med00-ogs-pft-an-fc-d_202003 ;;
	   "CO2F" ) dataset=med00-ogs-co2-an-fc-d_202003 ;;
	   * )  echo Wrong type ; usage; exit 1 ;;
	esac
    echo "    <dataset DatasetName=\"${dataset}\">" >> $DNT_FILE

	for month in `seq 1 12 `; do
	   mm=`printf %02d $month `
	   to_remove_dir=${year}/${mm}
	   DELETE_STR="<directory SourceFolderName=\"${to_remove_dir}\" DestinationFolderName=\"\"  > <KeyWord>Delete</KeyWord> </directory>"
	   echo "             $DELETE_STR"  >> $DNT_FILE
	done
   echo "    </dataset>"  >> $DNT_FILE


done

echo "</delivery>" >> $DNT_FILE

echo "Now send $DNT_FILE"