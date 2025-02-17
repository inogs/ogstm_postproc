#! /bin/bash

YEAR=2021 # not important here, not passed from job
. ../profile.inc
. ./config.sh -y $YEAR

rm -rf $VALIDATION_DIR/SAT
mkdir -p $VALIDATION_DIR/SAT

my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/pfts"
cd $BITSEA/src/bitsea/validation/deliverables/

PERIOD="-s 19990101 -e 20200101"

#16 subbasins
for VAR in   P_l  P1l    P2l    P3l    P4l kd490 RRS412    RRS443    RRS490    RRS510    RRS555    RRS670 ; do
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}"

   
   my_prex_or_die "python plot_timeseries_STD.py      -v $VAR -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR} -c open_sea $PERIOD"
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}   -c open_sea $PERIOD" # table4.1

done

for VAR in   P_l  P1l    P2l    P3l    P4l kd490 RRS412    RRS443    RRS490    RRS510    RRS555    RRS670 ; do
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/Rivers/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/Rivers/${VAR}"

 
   my_prex_or_die "python plot_timeseries_STD.py      -v $VAR -i $SAT_VALID_DIR/RIVERS -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/Rivers/${VAR} -c everywhere $PERIOD"
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $SAT_VALID_DIR/RIVERS -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/Rivers/${VAR}   -c everywhere $PERIOD" # table4.1

done






my_prex_or_die "python plot_pfts.py -i $SAT_VALID_DIR -o $VALIDATION_DIR/SAT/pfts/ -s $PERIOD"