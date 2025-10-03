#! /bin/bash

FREQUENCY=daily

function dataset_substr {
#  returns BIOL, CARB, ...

   filename=$1
   basenamefile=$( basename $filename )
   echo ${basenamefile:16:4}
}

function get_dataset {
#  get_dataset BIOL monthly returns med-ogs-bio-an-fc-m
   parameter=$1
   frequency=$2
   case $frequency in
    daily )  time_flag=D ;;
   monthly)  time_flag=M ;;
   *) echo "ERROR"; exit 1 ;;
   esac

   case $parameter in
   BIOL) DATASET=cmems_mod_med_bgc-bio_anfc_4.2km_P1${time_flag}-m ;;
   CARB) DATASET=cmems_mod_med_bgc-car_anfc_4.2km_P1${time_flag}-m ;;
   NUTR) DATASET=cmems_mod_med_bgc-nut_anfc_4.2km_P1${time_flag}-m ;;
   PFTC) DATASET=cmems_mod_med_bgc-pft_anfc_4.2km_P1${time_flag}-m ;;
   CO2F) DATASET=cmems_mod_med_bgc-co2_anfc_4.2km_P1${time_flag}-m ;;
   EXCO) DATASET=cmems_mod_med_bgc-optics_anfc_4.2km_P1${time_flag}-m ;;
   *)  echo "ERROR"; exit 1 ;;
   esac
   echo $DATASET
}


function print_file_attr {
  filename=$1
  dataset_substring=`dataset_substr $filename`
  DATASET=`get_dataset $dataset_substring $FREQUENCY `

  echo ""
  echo "PRODUCT MEDSEA_ANALYSISFORECAST_BGC_006_014"
  echo "Dataset: $DATASET"
  echo "File: " $( basename $1 )

}


function try_send {
  ZIPPED_DIR=/pico/scratch/userexternal/gbolzon0/REANALYSIS_2016/wrkdir/POSTPROC/output/ZIPPED
  basenamefile=$( basename ${1} )
  [[ $basenamefile == *BIOL* ]] && DATASET=sv03-med-ogs-bio-rean-m
  [[ $basenamefile == *CARB* ]] && DATASET=sv03-med-ogs-car-rean-m
  [[ $basenamefile == *NUTR* ]] && DATASET=sv03-med-ogs-nut-rean-m
  [[ $basenamefile == *PFTC* ]] && DATASET=sv03-med-ogs-pft-rean-m
  
  PRODUCT=MEDSEA_REANALYSIS_BIO_006_008
  echo ""
  echo "ncftpput -u bio_a -p XXX -P 2120 upload.cmems-med-mfc.eu ${PRODUCT}/${DATASET} ${basenamefile}.gz > /dev/null 2>&1 && echo OK "
  ncftpput -u bio_a -p 5a2cf6cd95Q! -P 2120 upload.cmems-med-mfc.eu ${PRODUCT}/${DATASET} ${ZIPPED_DIR}/${basenamefile}.gz > /dev/null 2>&1 && echo OK
  
}


function file_format_check {
  # PU_OP_TF_FileFormat 
  ncdump -h ${1} >/dev/null 2>&1
  [ $? = 0 ] && echo OK
}

function title_check {
#PU_IT_TF_DatasetTitle
ncdump -h ${1} | grep -w ":title = " | cut -d= -f2
}


function dim_check {
#PU_IT_TF_VarDimension
variable=$2
 ncdump -h ${1}  | grep -w $variable |grep -v ":"
}


function ncattget { 
ncks -M -m ${3} | grep -E -i "^${2} attribute [0-9]+: ${1}" | cut -f 11- -d ' ' | sort 
 }
function ncattget {
ncks -M -m ${3} | grep ${2} | grep ${1} | awk '{print $3}' | cut -d "f" -f 1
}


PIT=$HOME/CMEMS-MED-PIT-v202211_GB.xlsx
DIR=/g100_scratch/userexternal/gbolzon0/V9C/PRODOTTI/NRT/PRODOTTI/
TIME_TO_CHECK=20190501




if [ 1 == 1 ] ; then


echo "#####  PU_OP_TF_FileFormat "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 print_file_attr $filename
 file_format_check $filename
done



echo "#####  PU_IT_TF_DatasetTitle "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
  dataset_substring=`dataset_substr $filename`
  DATASET=`get_dataset $dataset_substring $FREQUENCY`
  python check_title.py -f $filename -p $PIT -d $DATASET
done

fi



if [ 1 == 1 ] ; then

echo "#####  PU_IT_TF_VarDimension   "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
  print_file_attr $filename
  if echo $filename | grep -q BIOL ; then
     dim_check $filename o2
     dim_check $filename nppv
  fi
  if echo $filename | grep -q CARB ; then
     dim_check $filename ph
     dim_check $filename dissic
     dim_check $filename talk
  fi 
  if echo $filename | grep -q NUTR ; then
     dim_check $filename no3
     dim_check $filename po4
     dim_check $filename nh4
     dim_check $filename si
  fi  
  if echo $filename | grep -q PFTC ; then
     dim_check $filename phyc
     dim_check $filename chl
     dim_check $filename zooc
  fi
  if echo $filename | grep -q CO2F ; then
     dim_check $filename fgco2
     dim_check $filename spco2
  fi  
done


fi
if [ 1 == 1 ] ; then


echo "#####  PU_IT_TF_VarLimits   "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
   print_file_attr $filename
   for var in longitude latitude depth ; do
      themin=`ncattget valid_min $var $filename`
      themax=`ncattget valid_max $var $filename`
      echo "$var" valid_min $themin
      echo "$var" valid_max $themax
   done
   
done 


exit 0

echo "####   STATIC FILES ####"
echo ""

filename=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/POSTPROC/bin_prod/prodotti/MED_MFC_006_014_coordinates.nc
echo "PRODUCT MEDSEA_ANALYSISFORECAST_BGC_006_014"
echo $filename
file_format_check $filename
dim_check $filename e1t
dim_check $filename e2t
dim_check $filename e3t

echo "PRODUCT MEDSEA_ANALYSISFORECAST_BGC_006_014"
filename=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/POSTPROC/bin_prod/prodotti/MED_MFC_006_014_mask_bathy.nc
echo $filename
file_format_check $filename
dim_check $filename mask
dim_check $filename deptho
dim_check $filename deptho_lev


exit 0


for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 try_send $filename
done


fi



