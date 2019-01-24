#! /bin/bash

usage() {
echo "Parallel zip and tar RST directory of ogstm. "
echo "The dataset in the input directory, a list of RST.date17.var.nc is archived"
echo "in the output directory by variable, as date1.tar, date2.tar ..."
echo "each one contanining all the variables as compressed files"
echo "SYNOPSYS"
echo "tar_rstdir.sh [ -i RSTDIR] [-o TARDIR ] [-n NCPUS]"
}


if [ $# -lt 6 ] ; then
  usage
  exit 1
fi

for I in 1 2 3 ; do
case $1 in
"-i" ) INPUT_RSTDIR=$2;;
"-o" ) OUTPUT_TARDIR=$2;;
"-n" ) NCPUS=$2;;
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
mpirun -np $NCPUS python compress.py -i ${INPUT_RSTDIR} -o ${ZIPPED_DIR} -l RST*nc
ANS=$?

if [ $ANS -eq 0 ] ; then
   echo "${INPUT_RSTDIR} has been compressed" 
else
   echo "Error in compresson of ${INPUT_RSTDIR}"
   exit 1
fi 
date

# get timelist
cd ${INPUT_RSTDIR}
ls RST*N1p.nc | cut -c 5-12 > $HERE/rst_times.txt



# creating tars
cd $HERE
mpirun -np $NCPUS python packDA.py -i ${ZIPPED_DIR} -o ${OUTPUT_TARDIR} -v rst_times.txt
ANS=$?

if [ $ANS -eq 0 ] ; then
   echo "${ZIPPED_DIR} has been packed and removed"
   rm -rf ${ZIPPED_DIR}
   echo "${INPUT_RSTDIR} can be removed"
else
   echo "Error in tar generation of ${ZIPPED_AVEDIR}"
   exit 1
fi
date

 