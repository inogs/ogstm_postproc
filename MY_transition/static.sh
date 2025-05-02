#! /bin/bash

. ../profile.inc
. ./launch.sh

#rm -rf $VALIDATION_DIR/STATIC
mkdir -p $VALIDATION_DIR/STATIC

mkdir -p $VALIDATION_DIR/STATIC/EMODnet/everywhere
mkdir -p $VALIDATION_DIR/STATIC/EMODnet/OpenSea
mkdir -p $VALIDATION_DIR/STATIC/EMODnet/OpenSea/Tables/

for var in ALK DIC N1p N3n N4n N5s O2o pH pCO2 ; do
    mkdir -p $VALIDATION_DIR/STATIC/EMODnet/OpenSea/Tables/${var}
done
mkdir -p $VALIDATION_DIR/STATIC/Socat/
mkdir -p $VALIDATION_DIR/STATIC/HPLC/

cd $BITSEA/validation/deliverables


INDIR_HPLC_CLIM=/g100_work/OGS_devC/Benchmark/SETUP/POSTPROC/HPLC
for var in P1l P2l P3l P4l ; do
    my_prex_or_die "python plot_HPLC_clim.py -i $INDIR_HPLC_CLIM -p $var -o $VALIDATION_DIR/STATIC/HPLC "
done

exit 0


# COMPARISON WITH EMODnet CLIMATOLOGY:
my_prex_or_die "python simulation_vs_clim_extended.py  -i $STAT_PROFILES_DIR -o $VALIDATION_DIR/STATIC/EMODnet/everywhere -s 20190101 -e 20200101 -m $MASKFILE"
my_prex_or_die "python simulation_vs_clim_extended_OpenSea.py -i $STAT_PROFILES_DIR -o $VALIDATION_DIR/STATIC/EMODnet/OpenSea -s 20190101 -e 20200101 -m $MASKFILE"


mkdir -p local_emodnet
my_prex_or_die "python static_clim_validation_OpenSea.py -i $STAT_PROFILES_DIR -o local_emodnet -m $MASKFILE -s 20190101 -e 20200101"


for var in ALK DIC N1p N3n N4n N5s O2o pH pCO2 ; do
   my_prex "mv local_emodnet/*${var}*.txt $VALIDATION_DIR/STATIC/EMODnet/OpenSea/Tables/${var}/"
done



mkdir -p local_socat
my_prex_or_die "python monthly_clim_socat_pCO2.py -o local_socat"                     # --> monthly_clim.socat, monthly_clim_socat_STD.txt, monthly_num_socat.txt
my_prex_or_die "python monthly_surf.py -i $STAT_PROFILES_DIR -y 2019 -o local_socat"  # -->monthly_var.txt
my_prex_or_die "python table_pCO2vsSOCAT.py -i local_socat -o $VALIDATION_DIR/STATIC/Socat/ " # monthly_pCO2.txt, monthly_clim_socat.txt monthly_num_socat.txt --> table.py --> pCO2-SURF-M-CLASS4-CLIM-RMSD-BASIN.txt,TOT_RMSD_pCO2vsSOCAT.txt


my_prex_or_die "python plot_month_pCO2vsSOCAT.py -i local_socat -o $VALIDATION_DIR/STATIC/Socat/ "  # monthly_clim_socat.txt, monthly_2019_surf/monthly_pCO2.txt --> plot.py --> pCO2_monthly_tseries_Fig4.20.png


