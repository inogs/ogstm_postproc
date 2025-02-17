#! /bin/bash


# Get the directory where this script is saved. This fails if the directory is
# a symlink or if we use ksh instead of bash. It must be executed at the begining
# of the script (or before we change the working dir)
BENCHMARK_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

. ../profile.inc
. ./launch.sh

rm -rf $VALIDATION_DIR/TIMESERIES
mkdir -p $VALIDATION_DIR/TIMESERIES


my_prex_or_die "python ../draw_timeseries.py -o ${VALIDATION_DIR}/TIMESERIES -m $MASKFILE -f timeseries_user_settings.txt"



# moving optical variables in TIMESERIES/optics/
mkdir -p $VALIDATION_DIR/TIMESERIES/optics
VARLIST="
        theta_chl
	theta_P1
	theta_P2
	theta_P3
	theta_P4
	limPAR_P1
	limPAR_P2
	limPAR_P3
	limPAR_P4"

for var in $VARLIST ; do
     [[ -d $VALIDATION_DIR/TIMESERIES/${var} ]] && mv $VALIDATION_DIR/TIMESERIES/${var}/ $VALIDATION_DIR/TIMESERIES/optics/
done
