#! /bin/bash

. ../profile.inc
. ./launch.sh -y 2021

rm -rf $VALIDATION_DIR/FLOAT
mkdir -p $VALIDATION_DIR/FLOAT

mkdir -p $VALIDATION_DIR/FLOAT/Hov/P_l
mkdir -p $VALIDATION_DIR/FLOAT/Hov/N3n
mkdir -p $VALIDATION_DIR/FLOAT/Hov/O2o
mkdir -p $VALIDATION_DIR/FLOAT/Hov/P_c

mkdir -p $VALIDATION_DIR/FLOAT/Key-processes/P_l
mkdir -p $VALIDATION_DIR/FLOAT/Key-processes/N3n
mkdir -p $VALIDATION_DIR/FLOAT/Key-processes/O2o
mkdir -p $VALIDATION_DIR/FLOAT/Key-processes/P_c

mkdir -p $VALIDATION_DIR/FLOAT/Weekly/P_l
mkdir -p $VALIDATION_DIR/FLOAT/Weekly/N3n
mkdir -p $VALIDATION_DIR/FLOAT/Weekly/O2o
mkdir -p $VALIDATION_DIR/FLOAT/Weekly/P_c
mkdir -p $VALIDATION_DIR/FLOAT/Weekly/POC



TMPDIR=$PWD/tmp_nc
TMPFILE=$PWD/float_bias_rmse.nc

cd $BITSEA/src/bitsea/validation/deliverables
mkdir -p $TMPDIR

my_prex_or_die "python SingleFloat_vs_Model_Stat_Timeseries.py -m $MASKFILE -b $BASEDIR -o $TMPDIR"
my_prex_or_die "python Hov_Stat_plot.py -m $MASKFILE -i $TMPDIR -b $BASEDIR -o $VALIDATION_DIR/FLOAT/Hov/P_l"

my_prex "mv $VALIDATION_DIR/FLOAT/Hov/P_l/*N3n*.png $VALIDATION_DIR/FLOAT/Hov/N3n"
my_prex "mv $VALIDATION_DIR/FLOAT/Hov/P_l/*O2o*.png $VALIDATION_DIR/FLOAT/Hov/O2o"
my_prex "mv $VALIDATION_DIR/FLOAT/Hov/P_l/*P_c*.png $VALIDATION_DIR/FLOAT/Hov/P_c"
#------------------------------------------------------
# Statistics about key processes for different basins
#
# Figures 4.6 and 4.13 + tables 4.4 and 4.8
# CHL-PROF-D-CLASS4-PROF-CORR-BASIN
# NIT-PROF-D-CLASS4-PROF-CORR-BASIN
#  DO-PROF-D-CLASS4-PROF-CORR-BASIN 


my_prex_or_die "python BASIN_Float_vs_Model_Stat_Timeseries_monthly.py -m $MASKFILE -b $BASEDIR -o $TMPDIR"

my_prex_or_die "python BASIN_Float_vs_Model_Stat_Timeseries_monthly_plotter.py -m $MASKFILE -i $TMPDIR -b $BASEDIR -o $VALIDATION_DIR/FLOAT/Key-processes/P_l"
my_prex "mv $VALIDATION_DIR/FLOAT/Key-processes/P_l/*N3n* $VALIDATION_DIR/FLOAT/Key-processes/N3n/"
my_prex "mv $VALIDATION_DIR/FLOAT/Key-processes/P_l/*O2o* $VALIDATION_DIR/FLOAT/Key-processes/O2o/"
my_prex "mv $VALIDATION_DIR/FLOAT/Key-processes/P_l/*P_c* $VALIDATION_DIR/FLOAT/Key-processes/P_c/"

#-----------------------------------------
# BIAS and RMSD averaged on BASIN:
#
# BIOFLOATS SECTION: statistics on layers
# CHL-LAYER-D-CLASS4-PROF-[BIAS/RMS]-BASIN
# NIT-LAYER-D-CLASS4-PROF-[BIAS/RMS]-BASIN
#  DO-LAYER-D-CLASS4-PROF-[BIAS/RMS]-BASIN


my_prex_or_die "python biofloats_ms.py  -m $MASKFILE -b $BASEDIR -o $TMPFILE"

for var in P_l N3n O2o P_c ; do
    my_prex_or_die "python biofloats_ms_plotter.py -b $BASEDIR -i $TMPFILE -o $VALIDATION_DIR/FLOAT/Weekly/$var -v $var"
done

