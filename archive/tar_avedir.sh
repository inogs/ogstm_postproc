#! /bin/bash

usage() {
echo "Parallel zip and tar AVE directory of ogstm. "
echo "The dataset in the input directory, a list of ave.date17.var.nc is archived"
echo "in the output directory by variable, as N1p.tar, N3n.tar ..."
echo "each one contanining all the time series of compressed files"
echo "SYNOPSYS"
echo "tar_avedir.sh [ -i AVEDIR] [-o TARDIR ] [-n NCPUS] [ -v REF_VAR] "
echo "REF_VAR is a name , e.g. N1p, of a variable existing in AVEDIR"
}


if [ $# -lt 8 ] ; then
  usage
  exit 1
fi

for I in 1 2 3 4; do
case $1 in
"-i" ) INPUT_AVEDIR=$2;;
"-o" ) OUTPUT_TARDIR=$2;;
"-n" ) NCPUS=$2;;
"-v" ) REF_VAR=$2;;
*  ) echo "Unrecognized option $1." ; usage;  exit 1;;
esac
shift 2
done


HERE=$PWD
ZIPPED_DIR=${OUTPUT_TARDIR}/zipped
mkdir -p $ZIPPED_DIR
mkdir -p $OUTPUT_TARDIR

date
echo "Start compression"
mpirun -np $NCPUS python netcdf4_compress.py -i ${INPUT_AVEDIR} -o ${ZIPPED_DIR} -l ave*nc
ANS=$?

if [ $ANS -eq 0 ] ; then
   echo "${INPUT_AVEDIR} has been compressed" 
else
   echo "Error in compresson of ${INPUT_AVEDIR}"
   exit 1
fi 
date

# get varlist
cd ${INPUT_AVEDIR}
FIRST_TIME=`ls ave*${REF_VAR}.nc | head -1 | cut -c 1-22`
ls ${FIRST_TIME}*nc | cut -d "." -f 3  > $HERE/allvarlist.txt


# creating tars
cd $HERE
mpirun -np $NCPUS python pack.py -i ${ZIPPED_DIR} -o ${OUTPUT_TARDIR} -v allvarlist.txt
ANS=$?

if [ $ANS -eq 0 ] ; then
   echo "${ZIPPED_DIR} has been packed and removed"
   rm -rf $ZIPPED_DIR
   echo "${INPUT_AVEDIR} can be removed"
else
   echo "Error in tar generation of ${ZIPPED_AVEDIR}"
   exit 1
fi
date

 
