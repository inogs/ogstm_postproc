#! /bin/bash

YEAR=2021 # not important here, not passed from job
. ../profile.inc
. ./config.sh -y $YEAR

rm -rf $VALIDATION_DIR/SAT
mkdir -p $VALIDATION_DIR/SAT

my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.1_offshore"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.2_coast"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/pfts"

cd $BITSEA/src/bitsea/validation/deliverables/

for VAR in   P_l  P1l    P2l    P3l    P4l kd490; do
   COMMONS="-i $SAT_VALID_DIR/16_SUBBASINS -v $VAR -s 20220101 -e 20250101"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}"


   my_prex_or_die "python plot_timeseries_STD.py      $COMMONS -c open_sea -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR} "
   my_prex_or_die "python plot_timeseries_RMS_CORR.py $COMMONS -c open_sea -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}" # table4.1
   my_prex_or_die "python plot_timeseries_RMS_CORR.py $COMMONS -c coast    -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}"  # table4.2

   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}/table4.1_${VAR}.txt $VALIDATION_DIR/SAT/table4.1_offshore "
   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}/table4.1_${VAR}.txt    $VALIDATION_DIR/SAT/table4.2_coast/table4.2_${VAR}.txt "

done

for VAR in   P_l ; do
   COMMONS="-i $SAT_VALID_DIR/RIVERS -v $VAR -s 20220101 -e 20250101"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/Rivers/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/Rivers/${VAR}"

   my_prex_or_die "python plot_timeseries_STD.py      $COMMONS -c everywhere -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/Rivers/${VAR} -z rivers"
   my_prex_or_die "python plot_timeseries_RMS_CORR.py $COMMONS -c everywhere -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/Rivers/${VAR} -z rivers " # table4.1

done


my_prex_or_die "python plot_pfts.py -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/pfts/ -s 20220101 -e 20250101"
