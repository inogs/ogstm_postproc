#! /bin/bash


#SBATCH --job-name=POST
#SBATCH -N2
#SBATCH --ntasks-per-node=36
#SBATCH --time=1:30:00
#SBATCH --mem=300gb
#SBATCH --account=OGS_test2528
#SBATCH --partition=g100_usr_prod
##SBATCH --qos=dcgp_qos_dbg

unset I_MPI_PMI_LIBRARY

. ../../profile.inc
source /g100_work/OGS23_PRACE_IT/COPERNICUS/sequence.sh

MASKFILE=/g100_work/OGS_prod2528/OPA/Interim-dev/etc/static-data/MED24_125/meshmask.nc
BULLDATE=20260820

INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/MODEL/AVE_FREQ_1
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/POSTPROC/output/PRODUCTS/DAILY/RE
mkdir -p $OUTPUTDIR
my_prex_or_die "python TimeList_generator.py -s 20230601-00:00:00 -e 20250731-00:00:00 --days 1 > timelist_daily_re"
my_prex_or_die "mpirun python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist_daily_re -m $MASKFILE -b $BULLDATE --tr daily --bulltype analysis"


OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/POSTPROC/output/PRODUCTS/DAILY/IN
mkdir -p $OUTPUTDIR
my_prex_or_die "python TimeList_generator.py -s 20250801-00:00:00 -e 20260731-12:00:00 --days 1 > timelist_daily_in"
my_prex_or_die "mpirun python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist_daily_in -m $MASKFILE -b $BULLDATE --tr daily --bulltype interim"

INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/POSTPROC/output/MONTHLY/AVE
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/POSTPROC/output/PRODUCTS/MONTHLY/RE
mkdir -p $OUTPUTDIR

my_prex_or_die "python TimeList_generator.py -s 20230601-00:00:00 -e 20250731-00:00:00 --months 1 > timelist_monthly_re"
my_prex_or_die "mpirun python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist_monthly_re -m $MASKFILE -b $BULLDATE --tr monthly --bulltype analysis"

OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/wrkdir/POSTPROC/output/PRODUCTS/MONTHLY/IN
mkdir -p $OUTPUTDIR
my_prex_or_die "python TimeList_generator.py -s 20250801-00:00:00 -e 20260731-12:00:00 --months 1 > timelist_monthly_in"
my_prex_or_die "mpirun python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist_monthly_in -m $MASKFILE -b $BULLDATE --tr monthly --bulltype interim"


exit 0



INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/MONTHLY
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/CLIM
MASKFILE=/g100_scratch/userexternal/gbolzon0/RA_24/meshmask.nc

for var in N1p N3n N4n P_c P_l O2o ppn pH O3c O3h CO2airflux pCO2 ; do
 my_prex_or_die "mpirun -np 12 python clim_generator.py -i $INPUTDIR -o $OUTPUTDIR -m $MASKFILE -v $var"
done


INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/CLIM
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/CLIM

my_prex_or_die "python prodotti_copernicus_rea_clim.py -i $INPUTDIR -o $OUTPUTDIR -m $MASKFILE -b 20221013"



