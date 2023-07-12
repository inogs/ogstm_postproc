#! /bin/bash

. ../profile.inc
. ./launch.sh

rm -rf $VALIDATION_DIR/TIMESERIES
mkdir -p $VALIDATION_DIR/TIMESERIES


cd $BITSEA/validation/deliverables


my_prex_or_die "python profiles_plotter.py -o $VALIDATION_DIR/TIMESERIES -m $MASKFILE -f profiles_plotter_user_settings.txt"
