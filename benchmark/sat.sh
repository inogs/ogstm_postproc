#! /bin/bash

. ../profile.inc
. ./launch.sh

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/
export MASKFILE


KD_MODEL_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/KD_WEEKLY/
SAT_KD_WEEKLY_DIR=/g100_work/OGS_devC/Benchmark/SETUP/POSTPROC/SAT/KD/WEEKLY_4_24
SAT_CHLWEEKLY_DIR=/g100_work/OGS_devC/Benchmark/SETUP/POSTPROC/SAT/CHL/WEEKLY_4_24

rm -rf $VALIDATION_DIR/SAT
mkdir -p $VALIDATION_DIR/SAT


my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.1_offshore"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/table4.2_coast"
my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/pfts"


for VAR in kd490 P_l  P1l    P2l    P3l    P4l  ; do
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}"
   my_prex_or_die "mkdir -p $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}"

   OPENSEA_PKL=${VAR}_open_sea.pkl
     COAST_PKL=${VAR}_coast.pkl

   MODELDIR=$INPUTDIR
   SAT_DIR=$SAT_CHLWEEKLY_DIR
   if [ $VAR == 'kd490' ] ; then 
        MODELDIR=$KD_MODEL_DIR
        SAT_DIR=$SAT_KD_WEEKLY_DIR
    fi

   LAYER=10
   # if [ $VAR == 'kd490' ] ; then LAYER=0 ; fi
   
   cd $BITSEA/validation/deliverables/
   
   my_prex_or_die "python ScMYvalidation_plan.py -v $VAR -s $SAT_DIR -i $MODELDIR -m $MASKFILE -c open_sea -l $LAYER  -o $OPENSEA_PKL"
   my_prex_or_die "python ScMYvalidation_plan.py -v $VAR -s $SAT_DIR -i $MODELDIR -m $MASKFILE -c coast    -l $LAYER  -o $COAST_PKL"
   my_prex_or_die "python plot_timeseries_STD.py -v $VAR -i $OPENSEA_PKL -o $VALIDATION_DIR/SAT/Fig4.2_Timeseries/offshore/${VAR}"
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $OPENSEA_PKL -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR} " # table4.1
   my_prex_or_die "python plot_timeseries_RMS_CORR.py -v $VAR -i $COAST_PKL -o $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}  "   # table4.2
   
   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/offshore/${VAR}/table4.1_${VAR}.txt $VALIDATION_DIR/SAT/table4.1_offshore "
   my_prex_or_die "cp $VALIDATION_DIR/SAT/Fig4.3_BiasRmsd/coast/${VAR}/table4.1_${VAR}.txt    $VALIDATION_DIR/SAT/table4.2_coast/table4.2_${VAR}.txt "

done


my_prex_or_die "python plot_pfts.py -i $PWD -o $VALIDATION_DIR/SAT/pfts/ "
