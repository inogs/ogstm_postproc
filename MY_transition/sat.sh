#! /bin/bash

YEAR=2021 # not important here, not passed from job
. ../profile.inc
. ./launch.sh -y $YEAR

rm -rf $VALIDATION_DIR/SAT
mkdir -p $VALIDATION_DIR/SAT

my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.1_offshore"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.2_coast"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/pfts"

for VAR in   P_l  P1l    P2l    P3l    P4l ; do
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}"

   cd $BITSEA/src/bitsea/validation/deliverables/

   my_prex_or_die "python plot_timeseries_STD.py -v $VAR -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR} -c open_sea -s 20210101 -e 20250101"
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $SAT_VALID_DIR -c open_sea -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR} -s 20210101 -e 20250101" # table4.1
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $SAT_VALID_DIR -c coast -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR} -s 20210101 -e 20250101"  # table4.2

   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}/table4.1_${VAR}.txt $VALIDATION_DIR/SAT/table4.1_offshore "
   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}/table4.1_${VAR}.txt    $VALIDATION_DIR/SAT/table4.2_coast/table4.2_${VAR}.txt "

done

my_prex_or_die "python plot_pfts.py -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/pfts/ "