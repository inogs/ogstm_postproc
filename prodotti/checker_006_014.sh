#! /bin/bash

function print_file_attr_d {
  basenamefile=$( basename ${1} )
  [[ $basenamefile == *BIOL* ]] && DATASET=med-ogs-bio-an-fc-d
  [[ $basenamefile == *CARB* ]] && DATASET=med-ogs-car-an-fc-d
  [[ $basenamefile == *NUTR* ]] && DATASET=med-ogs-nut-an-fc-d
  [[ $basenamefile == *PFTC* ]] && DATASET=med-ogs-pft-an-fc-d
  [[ $basenamefile == *CO2F* ]] && DATASET=med-ogs-co2-an-fc-d  
  
  echo ""
  echo "PRODUCT MEDSEA_ANALYSIS_FORECAST_BIO_006_014"
  echo "Dataset: $DATASET"
  echo "File: $basenamefile"

}

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

DIR=/gpfs/work/OGS18_PRACE_P_0/PROD_COPERNICUS/prodotti/MONTHLY/
TIME_TO_CHECK=20170101




if [ 1 == 1 ] ; then


echo "#####  PU_OP_TF_FileFormat "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 print_file_attr $filename
 file_format_check $filename
done



echo "#####  PU_IT_TF_DatasetTitle "
for filename in `ls $DIR/${TIME_TO_CHECK}*nc `; do
 print_file_attr $filename
 title_check $filename
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
     dim_check $filename pco
     dim_check $filename dic
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
     dim_check $filename co2airflux
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



