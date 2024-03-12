#! /bin/bash

. ../profile.inc
. ./launch.sh



INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1_tar

cd $INPUTDIR
for filename in $(ls ${TARDIR}/*.tar) ; do
    echo "Unarchiving ${filename}"
    tar -xf ${filename}
done


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2_tar

cd $INPUTDIR
for filename in $(ls ${TARDIR}/*.tar) ; do
    echo "Unarchiving ${filename}"
    tar -xf ${filename}
done


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar

cd $INPUTDIR
for filename in $(ls ${TARDIR}/*.tar) ; do
    echo "Unarchiving ${filename}"
    tar -xf ${filename}
done


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS_tar

cd $INPUTDIR

for filename in $(ls ${TARDIR}/*.tar) ; do
    echo "Unarchiving ${filename}"
    tar -xf ${filename}
done

