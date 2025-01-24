#! /bin/bash

usage() {
echo "SYNOPSYS"
echo "clean.sh -y YEAR"
echo "To be executed after NetCDF compression and tar generation"
echo "Removing original ave uncompressed files"
echo "Removing some of them with compressed ones"
}

if [ $# -lt 2 ] ; then
  usage
  exit 1
fi

case $1 in
      "-y" ) YEAR=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
esac
shift 2

. ../profile.inc
. ./launch.sh -y ${YEAR}



INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1_tar/${YEAR}

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc
cd $CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/
VARLIST="
N3n
N1p
N4n
N5s
P_c
P1c
P2c
P3c
P4c
P1l
P2l
P3l
P4l
P_l
Z3c
Z4c
Z5c
Z6c
O2o
ppn
pH
O3c
O3h
pCO2
"
for var in $VARLIST ; do
    echo "Unarchiving $var"
    my_prex_or_die "tar -xf ../AVE_FREQ_1_tar/${YEAR}/${var}.tar"
done



INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2_tar/${YEAR}

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc ave*bkp;
cd $CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/
for var in N1p N3n O2o P_l P_c O3c O3h DIC ALK ppn P1l P2l P3l P4l; do
    echo "Unarchiving $var"
     my_prex_or_die "tar -xf ../AVE_FREQ_2_tar/${YEAR}/${var}.tar"
done


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS_tar/${YEAR}

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f RST*nc

echo "You can archive with a serial job: AVE_FREQ_1_tar/${YEAR}, AVE_FREQ_2_tar/${YEAR}, AVE_FREQ_3_tar/${YEAR}, RESTARTS_tar/${YEAR}."
