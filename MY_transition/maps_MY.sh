#! /bin/bash

usage() {
echo "SYNOPSIS"
echo "./maps.sh -y [ YEAR ]"
}

if [ $# -lt 2 ] ; then
  usage
  exit 1
fi
YEAR=$2
YEAR_E=$(($(date -d "Jan 01, $YEAR" +"%Y") + 2))
# End year is YEAR_E, in total we consider 3 years.
echo $YEAR_E

. ../profile.inc
. ./config.sh -y $YEAR

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/YEARLY


mkdir -p $VALIDATION_DIR/MAPS/P_l/MY
mkdir -p $VALIDATION_DIR/MAPS/ppn/
mkdir -p $VALIDATION_DIR/MAPS/P_c/
mkdir -p $VALIDATION_DIR/MAPS/Z_c/


cd $BITSEA/src/bitsea/validation/deliverables

COMMONS_PARAMS="-m $MASKFILE  -l Plotlist_bio.xml -s ${YEAR}0101 -e ${YEAR_E}1231"

#my_prex_or_die "python averager_and_plot_map_ppn_refScale.py -i $INPUTDIR  -v ppn  -t integral  -o $VALIDATION_DIR/MAPS/ppn/ $COMMONS_PARAMS "
#there is also a table


#my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_l  -t mean -o $VALIDATION_DIR/MAPS/P_l $COMMONS_PARAMS "     # Fig4.1 CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_c  -t mean -m $MASKFILE -o  $VALIDATION_DIR/MAPS/P_c  -l Plotlist_bio_Int.xml -s ${YEAR}0101 -e ${YEAR_E}1231"
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v Z_c  -t integral -o  $VALIDATION_DIR/MAPS/Z_c   $COMMONS_PARAMS "

my_prex_or_die "python averager_and_plot_map_ppn_refScale_16basin_RMSD.py -i $INPUTDIR  -v ppn  -t integral -o $VALIDATION_DIR/MAPS/ppn $COMMONS_PARAMS "


#CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN from SATELLITE:
my_prex_or_die "python sat_ave_and_plot.py -i $SAT_CHLWEEKLY_DIR -m $MASKFILE  -o  $VALIDATION_DIR/MAPS/P_l/MY   -s ${YEAR}0101 -e ${YEAR_E}1231 "

#INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/
#INPUTDIR=
my_prex_or_die "python sat_model_RMSD_and_plot.py -s $SAT_CHLWEEKLY_DIR -i $INPUTDIR -m $MASKFILE -o $VALIDATION_DIR/MAPS/P_l/MY -st ${YEAR}0101 -e ${YEAR_E}1231"
