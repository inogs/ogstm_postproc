#! /bin/bash

. ../profile.inc
. ./launch.sh



INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1_tar

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc ;
for var in N1p N3n O2o P_l P_c O3c O3h DIC ALK ppn ; do
    echo "Unarchiving $var"
    tar -xf ../AVE_FREQ_1_tar/${var}.tar
done



INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2_tar

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc ave*bkp;
for var in N1p N3n O2o P_l P_c O3c O3h DIC ALK ppn P1l P2l P3l P4l; do
    echo "Unarchiving $var"
    tar -xf ../AVE_FREQ_2_tar/${var}.tar
done


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f ave*nc


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS_tar

cd $INPUTDIR
echo "Erasing original $INPUTDIR"
rm -f RST*nc

echo "You can archive with a serial job: AVE_FREQ_1_tar, AVE_FREQ_2_tar, AVE_FREQ_3_tar, RESTARTS_tar."