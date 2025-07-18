#! /bin/bash

usage() {
echo "SYNOPSIS"
echo "./maps_MY.sh -s [ YEAR1 ] -e [ YEAR2 ]"
}

if [ $# -lt 4 ] ; then
  usage
  exit 1
fi

for I in 1 2; do
   case $1 in
      "-s" ) YEAR1=$2;;
      "-e" ) YEAR2=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
   esac
   shift 2
done


. ../profile.inc
. ./config.sh -y $YEAR1

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/YEARLY


mkdir -p $VALIDATION_DIR/MAPS/P_l/MY
mkdir -p $VALIDATION_DIR/MAPS/ppn/
mkdir -p $VALIDATION_DIR/MAPS/P_c/
mkdir -p $VALIDATION_DIR/MAPS/Z_c/
mkdir -p $VALIDATION_DIR/MAPS/O2o/
mkdir -p $VALIDATION_DIR/MAPS/N1p/
mkdir -p $VALIDATION_DIR/MAPS/N3n/
mkdir -p $VALIDATION_DIR/MAPS/N4n/
mkdir -p $VALIDATION_DIR/MAPS/N5s/
mkdir -p $VALIDATION_DIR/MAPS/DIC/
mkdir -p $VALIDATION_DIR/MAPS/ALK/
mkdir -p $VALIDATION_DIR/MAPS/CO2airflux/


cd $BITSEA/src/bitsea/validation/deliverables

COMMONS_PARAMS="-m $MASKFILE  -l Plotlist_bio.xml -s ${YEAR1}0101 -e ${YEAR2}1231"

my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_l  -t mean -o $VALIDATION_DIR/MAPS/P_l $COMMONS_PARAMS "     # Fig4.1 CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v P_c  -t mean -m $MASKFILE -o  $VALIDATION_DIR/MAPS/P_c  -l Plotlist_bio_Int.xml -s ${YEAR1}0101 -e ${YEAR2}1231"
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v Z_c  -t integral -o  $VALIDATION_DIR/MAPS/Z_c   $COMMONS_PARAMS "

my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v O2o -t mean -m $VALIDATION_DIR/MAPS/O2o $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N1p -t mean -m $VALIDATION_DIR/MAPS/N1p $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N3n -t mean -m $VALIDATION_DIR/MAPS/N3n $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N4n -t mean -m $VALIDATION_DIR/MAPS/N4n $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v N5s -t mean -m $VALIDATION_DIR/MAPS/N5s $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v ALK -t mean -m $VALIDATION_DIR/MAPS/ALK $COMMONS_PARAMS "
my_prex_or_die "python averager_and_plot_map.py -i $INPUTDIR  -v DIC -t mean -m $VALIDATION_DIR/MAPS/DIC $COMMONS_PARAMS "

my_prex_or_die "python averager_and_plot_map_ppn.py -i $INPUTDIR  -v ppn  -t integral -o $VALIDATION_DIR/MAPS/ppn $COMMONS_PARAMS "


#CHL-LAYER-Y-CLASS1-[CLIM/LIT]-MEAN from SATELLITE:
my_prex_or_die "python sat_ave_and_plot.py -i $SAT_CHLWEEKLY_DIR -m $MASKFILE  -o  $VALIDATION_DIR/MAPS/P_l/MY   -s ${YEAR1}0101 -e ${YEAR2}1231 "


# Creating equivalent of MODEL/AVE_FREQ_2 after splitting on years
WEEKLY_DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/AVE_LINKS
mkdir -p $WEEKLY_DIR
cd $WEEKLY_DIR
for year in $(seq $YEAR1 $YEAR2); do
    for I in $(ls $CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${year}/ave*P_l.nc ) ; do
        ln -fs $I
    done
done

cd $BITSEA/src/bitsea/validation/deliverables

my_prex_or_die "python sat_model_RMSD_and_plot.py -s $SAT_CHLWEEKLY_DIR -i $WEEKLY_DIR -m $MASKFILE -o $VALIDATION_DIR/MAPS/P_l/MY -st ${YEAR1}0101 -e ${YEAR2}1231"
