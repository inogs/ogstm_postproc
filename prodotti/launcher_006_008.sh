#! /bin/bash


#SBATCH --job-name=POST
#SBATCH -N1
#SBATCH --ntasks-per-node=12
#SBATCH --time=01:30:00
#SBATCH --mem=100gb
#SBATCH --account=OGS_devC
#SBATCH --partition=g100_usr_prod
#SBATCH --qos=g100_qos_dbg

unset I_MPI_PMI_LIBRARY

. ../profile.inc
INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/MONTHLY
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/CLIM
MASKFILE=/g100_scratch/userexternal/gbolzon0/RA_24/meshmask.nc

for var in N1p N3n N4n P_c P_l O2o ppn pH O3c O3h CO2airflux pCO2 ; do
 my_prex_or_die "mpirun -np 12 python clim_generator.py -i $INPUTDIR -o $OUTPUTDIR -m $MASKFILE -v $var"
done


INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/CLIM
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/CLIM

my_prex_or_die "python prodotti_copernicus_rea_clim.py -i $INPUTDIR -o $OUTPUTDIR -m $MASKFILE -b 20221013"

exit 0

INPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/AVE/YEARLY
OUTPUTDIR=/g100_scratch/userexternal/gbolzon0/RA_24/PRODUCTS/YEARLY

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.*N1p.nc | cut -c 5-21  > $HERE/timelist

cd $HERE

mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20221004 --tr yearly --bulltype analysis

exit 0

BASEDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/
INPUTDIR=$BASEDIR/AVE_FREQ_1/
OUTPUTDIR=/gpfs/scratch/userexternal/gcoidess/PRODOTTI/daily/ 
MASKFILE=$BASEDIR/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD
cd $INPUTDIR
ls ave.199901*N1p.nc | cut -c 5-12 > $HERE/timelist


mpirun -np 1 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20210323 --tr daily --bulltype analysis
