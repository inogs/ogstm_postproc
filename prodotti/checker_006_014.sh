#! /bin/bash

CHECKFOR=daily

function dataset_substr {
   filename=$1
   basenamefile=$( basename $filename )
   echo ${basenamefile:16:4}
}

function get_dataset {
   parameter=$1
   case $parameter in
   BIOL) DATASET=med00-ogs-bio-an-fc-d ;;
   CARB) DATASET=med00-ogs-car-an-fc-d ;;
   NUTR) DATASET=med00-ogs-nut-an-fc-d ;;
   PFTC) DATASET=med00-ogs-pft-an-fc-d ;;
   CO2F) DATASET=med00-ogs-co2-an-fc-d ;;
   *)  echo "ERROR"; exit 1 ;;
   esac
   echo $DATASET
}

if [ $CHECKFOR == monthly ] ; then
function print_file_attr {
  basenamefile=$( basename ${1} )
  [[ $basenamefile == *BIOL* ]] && DATASET=med-ogs-bio-an-fc-m
  [[ $basenamefile == *CARB* ]] && DATASET=med-ogs-car-an-fc-m
  [[ $basenamefile == *NUTR* ]] && DATASET=med-ogs-nut-an-fc-m
  [[ $basenamefile == *PFTC* ]] && DATASET=med-ogs-pft-an-fc-m
  [[ $basenamefile == *CO2F* ]] && DATASET=med-ogs-co2-an-fc-m
  
  echo ""
  echo "PRODUCT MEDSEA_ANALYSIS_FORECAST_BIO_006_014"
  echo "Dataset: $DATASET"
  echo "File: $basenamefile"

}

else

function print_file_attr {
  filename=$1
  dataset_substring=`dataset_substr $filename`
  DATASET=`get_dataset $dataset_substring`

  echo ""
  echo "PRODUCT MEDSEA_ANALYSIS_FORECAST_BIO_006_014"
  echo "Dataset: $DATASET"
  echo "File: " $( basename $1 )

}


fi

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


PIT=CMEMS-PIT-MED-202003.xlsx
DIR=/marconi_scratch/userexternal/gbolzon0/PROD/PRODOTTI/
TIME_TO_CHECK=20180101




if [ 1 == 1 ] ; then


echo "#####  PU_OP_TF_FileFormat "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 print_file_attr $filename
 file_format_check $filename
done



echo "#####  PU_IT_TF_DatasetTitle "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
  dataset_substring=`dataset_substr $filename`
  DATASET=`get_dataset $dataset_substring`
  #python check_title.py -f $filename -p $PIT -d $DATASET
done


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
  fi 
  if echo $filename | grep -q NUTR ; then
     dim_check $filename no3
     dim_check $filename po4
  fi  
  if echo $filename | grep -q PFTC ; then
     dim_check $filename phyc
     dim_check $filename chl
  fi
  if echo $filename | grep -q CO2F ; then
     dim_check $filename fpco2
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


for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 try_send $filename
done


fi



