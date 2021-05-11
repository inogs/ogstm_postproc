#! /bin/bash

#######     DNT_remove_generator.sh        #########
#        Generates delivery note xml file          #
#      to remove products from COPERNICUS DU       #
#                                                  #
#      Author: GB. 2020.02.27                      #
####################################################


usage() {
echo "Generates DNT files for removing product files from DU"
echo "Generated DNT removes both daily and associated monthly files"
echo "SYNOPSYS"
echo "DNT_remove_generator.sh  [ -y $YEAR ] [ -m $MONTH] [ -t TYPE ] "
echo ""
}

if [ $# -lt 3 ] ; then
  usage
  exit 1
fi

for I in 1 2 3; do
   case $1 in
      "-t" ) TYPE=$2;;
      "-y" ) yyyy=$2;;
      "-m" ) mm=$2;;      
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done



function decide_action {
   # arg1 = remote product file
   # returns in the exit_status a code for the actions to do

   # 1 means nothing to do
   # 2 means delete
   # 3 means error

   remotefile=$1

   remotebul_time=${remotefile:34:8}
       remotetype=${remotefile:43:2}

   if [[ $remotefile == "" ]]            ; then return 1 ; fi
   if ( [[ $remotetype == fc ]] || [[ $remotetype == sm ]]  )  ; then return 2 ; fi
   return 2
}

product=MEDSEA_ANALYSISFORECAST_BGC_006_014
logDir=.
case $TYPE in
   "BIOL" ) dataset=med-ogs-bio-an-fc-d_202105 ;;
   "CARB" ) dataset=med-ogs-car-an-fc-d_202105 ;;
   "NUTR" ) dataset=med-ogs-nut-an-fc-d_202105 ;;
   "PFTC" ) dataset=med-ogs-pft-an-fc-d_202105 ;;
   "CO2F" ) dataset=med-ogs-co2-an-fc-d_202105 ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac


DntTime=`date --utc +%Y%m%dT%H%M%SZ`
DNT_FILE=${logDir}/${product}_${DntTime}.xml

echo "<?xml version=\"1.0\" encoding=\"UTF-8\"?>" >  $DNT_FILE
echo "<delivery product=\"${product}\" PushingEntity=\"${PushingEntity}\" date=\"${DntTime}\">" >> $DNT_FILE
echo "    <dataset DatasetName=\"${dataset}\">" >> $DNT_FILE


upload_xml=False

DATELIST=$( python monthly_timelist_generator.py -y $yyyy -m $mm )

for day in $DATELIST ; do
  #---------------------------------------------------------
  remote_name=`./get_daily_product_in_DU.sh -d $day -t $TYPE`
  decide_action $remote_name
  ACTION=$?
  #---------------------------------------------------------
  
  case $ACTION in
  1) echo "$day $TYPE not in DU" ;;
  2) echo "$remote_name has to be deleted"
     upload_xml=True
  	 to_remove_file=$yyyy/$mm/$remote_name
	 DELETE_STR="<file FileName=\"${to_remove_file}\" > <KeyWord>Delete</KeyWord> </file>"
	 echo "             $DELETE_STR"  >> $DNT_FILE
	 ;;
  3) echo "ERROR: only analysis files are supposed to be removable" ;;
   *) echo "wrong decide_action exit status"; exit 1 ;;
 esac
  
done

echo "    </dataset>"  >> $DNT_FILE

########   Monthly Section     ###########

case $TYPE in
   "BIOL" ) dataset=med-ogs-bio-an-fc-m_202105 ;;
   "CARB" ) dataset=med-ogs-car-an-fc-m_202105 ;;
   "NUTR" ) dataset=med-ogs-nut-an-fc-m_202105 ;;
   "PFTC" ) dataset=med-ogs-pft-an-fc-m_202105 ;;
   "CO2F" ) dataset=med-ogs-co2-an-fc-m_202105 ;;
   * )  echo Wrong type ; usage; exit 1 ;;
esac
echo "    <dataset DatasetName=\"${dataset}\">" >> $DNT_FILE
remote_name=`./get_monthly_product_in_DU.sh -d $yyyy$mm -t $TYPE`
decide_action $remote_name
ACTION=$?
case $ACTION in
   1) echo "$day $TYPE not in DU" ;;
   2) echo "$remote_name has to be deleted"
      upload_xml=True
      to_remove_file=$yyyy/$remote_name
	  DELETE_STR="<file FileName=\"${to_remove_file}\" > <KeyWord>Delete</KeyWord> </file>"
	  echo "             $DELETE_STR"  >> $DNT_FILE
	  ;;
   3) echo "ERROR: only analysis files are supposed to be removable" ;;
   *) echo "wrong decide_action exit status"; exit 1 ;;
esac

echo "    </dataset>"  >> $DNT_FILE
echo "</delivery>" >> $DNT_FILE

if [ $upload_xml == "True" ] ; then
   echo "Now upload $DNT_FILE"
else
   echo "Don't upload $DNT_FILE"
fi

