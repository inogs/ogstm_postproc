#! /bin/bash

. ../profile.inc
. ./config.sh -y 2021

#rm -rf $VALIDATION_DIR/STATIC
mkdir -p $VALIDATION_DIR/STATIC

mkdir -p $VALIDATION_DIR/STATIC/MedBGCins/OpenSea
mkdir -p $VALIDATION_DIR/STATIC/MedBGCins/OpenSea/Tables/

for var in ALK DIC N1p N3n N4n N5s O2o pH pCO2 ; do
    mkdir -p $VALIDATION_DIR/STATIC/MedBGCins/OpenSea/Tables/${var}
done
mkdir -p $VALIDATION_DIR/STATIC/Socat/
mkdir -p $VALIDATION_DIR/STATIC/HPLC/

 TABLES_DIR=$VALIDATION_DIR/STATIC/HPLC/tables
FIGURES_DIR=$VALIDATION_DIR/STATIC/HPLC/figures
mkdir -p $TABLES_DIR $FIGURES_DIR

cd $BITSEA/src/bitsea/validation/deliverables/


# generates the csv files for model and ref data with mean and std values for med basin
# for summer and winter:
CLIMDIR=/g100_work/OGS_test2528/Observations/TIME_RAW_DATA/STATIC/HPLC
PARAMS="-c $CLIMDIR -m $MASKFILE -s 20220101 -e 20250101"
my_prex_or_die "python static_clim_validation_HPLC.py $PARAMS -i $STATPROFILESDIR -o $TABLES_DIR"

# plot the results for every pfts:
#INDIR_HPLC_CLIM=/g100_work/OGS_devC/Benchmark/SETUP/POSTPROC/HPLC
for var in P1l P2l P3l P4l ; do
    my_prex_or_die "python plot_HPLC_clim.py -i $TABLES_DIR -p $var -o $FIGURES_DIR "
done



# COMPARISON WITH MedBGCins CLIMATOLOGY:
CLIMDIR=/g100_work/OGS_test2528/Observations/TIME_RAW_DATA/STATIC/MedBGCins
PARAMS="-c $CLIMDIR  -s 20220101 -e 20250101 -m $MASKFILE"
my_prex_or_die "python simulation_vs_clim_extended_OpenSea.py $PARAMS -i $STATPROFILESDIR -o $VALIDATION_DIR/STATIC/MedBGCins/OpenSea"

LOCAL_MedBGCins=$PWD/local_MedBGCins
mkdir -p $LOCAL_MedBGCins
my_prex_or_die "python static_clim_validation_OpenSea.py $PARAMS -i $STATPROFILESDIR -o $LOCAL_MedBGCins"


for var in ALK DIC N1p N3n N4n N5s O2o pH pCO2 ; do
   my_prex "mv $LOCAL_MedBGCins/*${var}*.txt $VALIDATION_DIR/STATIC/MedBGCins/OpenSea/Tables/${var}/"
done


LOCAL_SOCAT=$PWD/local_socat
mkdir -p $LOCAL_SOCAT
#my_prex_or_die "python monthly_clim_socat_pCO2.py -o local_socat"                     # --> monthly_clim.socat, monthly_clim_socat_STD.txt, monthly_num_socat.txt
cp /g100_work/OGS_test2528/Observations/TIME_RAW_DATA/STATIC/CO2_socat/monthly_clim_socat.txt $LOCAL_SOCAT
cp /g100_work/OGS_test2528/Observations/TIME_RAW_DATA/STATIC/CO2_socat/monthly_num_socat.txt  $LOCAL_SOCAT
my_prex_or_die "python monthly_surf.py -i $STATPROFILESDIR -o $LOCAL_SOCAT"  # -->monthly_var.txt
my_prex_or_die "python table_pCO2vsSOCAT.py -i $LOCAL_SOCAT -o $VALIDATION_DIR/STATIC/Socat/ " # monthly_pCO2.txt, monthly_clim_socat.txt monthly_num_socat.txt --> table.py --> pCO2-SURF-M-CLASS4-CLIM-RMSD-BASIN.txt,TOT_RMSD_pCO2vsSOCAT.txt


my_prex_or_die "python plot_month_pCO2vsSOCAT.py -i $LOCAL_SOCAT -o $VALIDATION_DIR/STATIC/Socat/ "  # monthly_clim_socat.txt, monthly_2019_surf/monthly_pCO2.txt --> plot.py --> pCO2_monthly_tseries_Fig4.20.png


