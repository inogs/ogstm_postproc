#! /bin/bash


#SBATCH --job-name=POST
#SBATCH -N1
#SBATCH --ntasks-per-node=5
#SBATCH --time=0:30:00
#SBATCH --mem=100gb
#SBATCH --account=OGS_test2528_0
#SBATCH --partition=dcgp_usr_prod
#SBATCH --qos=dcgp_qos_dbg

unset I_MPI_PMI_LIBRARY

. ../profile.inc


INPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/AVE_DAILY
OUTPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/DAILY/RE
MASKFILE=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/meshmask.nc

mkdir -p $OUTPUTDIR
HERE=$PWD


cat<<EOF > timelist
20250801
20250802
20250803
20250804
20250805
EOF

#my_prex_or_die "mpirun -np 5 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20250901 --tr daily --bulltype analysis"


OUTPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/DAILY/IN
cat<<EOF > timelist
20250821
20250822
20250823
20250824
20250825
EOF

#my_prex_or_die "mpirun -np 5 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20250901 --tr daily --bulltype interim"

INPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/AVE_MONTHLY
OUTPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/MONTHLY/RE
cat<<EOF > timelist
20250101
20250201
20250301
20250401
20250501
EOF

my_prex_or_die "mpirun -np 5 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20250901 --tr monthly --bulltype analysis"

OUTPUTDIR=/leonardo_scratch/large/userexternal/gbolzon0/V12C/Samples/PROD/MONTHLY/IN
cat<<EOF > timelist
20250801
20250901
20251001
20251101
20251201
EOF

my_prex_or_die "mpirun -np 5 python prodotti_copernicus_rea.py -i $INPUTDIR -o $OUTPUTDIR -t timelist -m $MASKFILE -b 20250901 --tr monthly --bulltype interim"


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
