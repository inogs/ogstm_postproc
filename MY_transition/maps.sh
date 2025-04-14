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

. ../profile.inc
. ./config.sh -y $YEAR

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/YEARLY

mkdir -p $VALIDATION_DIR/MAPS
 

# CREATE MAP PPN INTEGRAL 0-200m 
mkdir -p $VALIDATION_DIR/MAPS/ppn/
mkdir -p $VALIDATION_DIR/MAPS/P_l
mkdir -p $VALIDATION_DIR/MAPS/N1p/
mkdir -p $VALIDATION_DIR/MAPS/N3n/
mkdir -p $VALIDATION_DIR/MAPS/O2o/
mkdir -p $VALIDATION_DIR/MAPS/ALK/
mkdir -p $VALIDATION_DIR/MAPS/DIC/
mkdir -p $VALIDATION_DIR/MAPS/P_c/
mkdir -p $VALIDATION_DIR/MAPS/ppn/
mkdir -p $VALIDATION_DIR/MAPS/Z_c/
mkdir -p $VALIDATION_DIR/MAPS/CO2airflux/

cd $BITSEA/src/bitsea/validation/deliverables/

COMMONS_PARAMS="-m $MASKFILE  -l Plotlist_bio.xml -s ${YEAR}0101 -e ${YEAR}1231"

#there is also a table for ppn
my_prex_or_die "python averager_and_plot_map_ppn_refScale_16basin_RMSD.py -i $INPUTDIR  -v ppn  -t integral -o $VALIDATION_DIR/MAPS/ppn $COMMONS_PARAMS "


my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_l  -t mean -o $VALIDATION_DIR/MAPS/P_l $COMMONS_PARAMS "     # Fig4.1 CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N3n  -t mean -o $VALIDATION_DIR/MAPS/N3n $COMMONS_PARAMS "     # Fig4.10 NIT-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N1p  -t mean -o $VALIDATION_DIR/MAPS/N1p $COMMONS_PARAMS "     # Fig4.9  PHOS-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_c  -t mean  -t mean -m $MASKFILE -o  $VALIDATION_DIR/MAPS/P_c  -l Plotlist_bio_Int.xml -s 20220101 -e 20250101"
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v Z_c  -t integral -m $MASKFILE -o  $VALIDATION_DIR/MAPS/Z_c  -l Plotlist_bio.xml -s 20220101 -e 20250101"
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v O2o  -t mean -o $VALIDATION_DIR/MAPS/O2o $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v CO2airflux -t mean -o $VALIDATION_DIR/MAPS/CO2airflux $COMMONS_PARAMS " 
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v CO2airflux -t mean -o $VALIDATION_DIR/MAPS/CO2airflux -m $MASKFILE  -l Plotlist_bio.xml -s 20220101 -e 20250101"
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v ALK  -t mean -o $VALIDATION_DIR/MAPS/ALK $COMMONS_PARAMS"      # Ac-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN  --> not requested in the ScQP
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v DIC  -t mean -o $VALIDATION_DIR/MAPS/DIC $COMMONS_PARAMS "     # DIC-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN --> not requested in the ScQP


#CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN from SATELLITE:
my_prex_or_die "python sat_ave_and_plot.py -i $SAT_CHLWEEKLY_DIR -m $MASKFILE  -o  $VALIDATION_DIR/MAPS/P_l   -s ${YEAR}0101 -e ${YEAR}1231 "

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/
my_prex_or_die "python sat_model_RMSD_and_plot.py -s $SAT_CHLWEEKLY_DIR -i $INPUTDIR -m $MASKFILE -o $VALIDATION_DIR/MAPS/P_l -st ${YEAR}0101 -e ${YEAR}1231"
