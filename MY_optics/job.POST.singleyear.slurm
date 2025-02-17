#! /bin/bash

#SBATCH --job-name=POST
#SBATCH -N5
#SBATCH --ntasks-per-node=24
#SBATCH --time=01:30:00
#SBATCH --mem=300gb
#SBATCH --account=OGS_devC
#SBATCH --partition=g100_meteo_prod
#SBATCH --qos=qos_meteo

usage() {
echo "SYNOPSYS"
echo "sbatch job.POST.singleyear.slurm -y YEAR"
echo "Caveat: the user has to have writing permissions on wrkdir/MODEL
echo "If not, use MODEL_linker.sh to generate a suitable wrkdir/MODEL
}

if [ $# -lt 2 ] ; then
  usage
  exit 1
fi

case $1 in
      "-y" ) YEAR=$2;;
        *  ) echo "Unrecognized option $1." ; usage;  exit 1;;
esac
shift 2

cd $SLURM_SUBMIT_DIR

. ../profile.inc
. ./config.sh -y ${YEAR}

unset I_MPI_PMI_LIBRARY
export UCX_TLS=ib
export SLURM_PMIX_DIRECT_CONN_UCX=false


export    MASKFILE=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/meshmask.nc
export  KCOASTFILE=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/mapser.npy

export PATH=$PATH:..



####### moving in year/ directories ################
MODEL_AVEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/
cd $MODEL_AVEDIR
rm -f AVE_FREQ_1/*nc
mkdir -p AVE_FREQ_2/${YEAR} AVE_FREQ_3/${YEAR} RESTARTS/${YEAR} 
cd AVE_FREQ_2
my_prex "mv ave.${YEAR}*.nc ${YEAR}/ "
rm -f ave.${YEAR}.nc.bkp

cd $MODEL_AVEDIR/AVE_FREQ_3
my_prex "mv ave.${YEAR}*.nc ${YEAR}/"

cd $MODEL_AVEDIR/RESTARTS
my_prex "mv RST.${YEAR}*.nc ${YEAR}/"


########  LOW FREQUENCY ######################################################

cd $SLURM_SUBMIT_DIR

MODEL_AVEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
      OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/



        TMPS=$OUTDIR/TMPS/${YEAR}
  CHLSUP_DIR=$OUTDIR/CHL_SUP

my_prex_or_die_with_tries "mpirun -np 120 python ../var_aggregator.py -l ave*N1p.nc -i $MODEL_AVEDIR -d VarDescriptor_2.xml -t $MODEL_AVEDIR -c $CHLSUP_DIR -m $MASKFILE"
my_prex_or_die_with_tries "mpirun -np 120 python ../metrics_2d.py -i $MODEL_AVEDIR -m $MASKFILE -o $MODEL_AVEDIR"

cd $MODEL_AVEDIR
for filename in metrics*; do
    date17=${filename:8:17}
    for var in dcm phosphocline nitracline; do
      ln -fs $filename ave.${date17}.${var}.nc
   done
done

cd $SLURM_SUBMIT_DIR
export BASINS=V2
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc     -i $MODEL_AVEDIR -f N1p -a $MODEL_AVEDIR -d VarDescriptor_2.xml -o $OUTDIR -t $TMPS  -s "
rm -rf $TMPS

my_prex_or_die_with_tries "mpirun -np 16 python ../compact_profiles.py -i $OUTDIR/STAT_PROFILES/ -o $OUTDIR/STAT_PROFILES/"

################## end of integrals/profiles stuff  ##############

################ Kd  #########################

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}
KD__DAILY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/KD_DAILY/${YEAR}
KD_WEEKLY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
BOTTOMDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/BOTTOM/${YEAR}
SURF__DIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/SURF/{$YEAR}

mkdir -p $BOTTOMDIR
mkdir -p $SURF__DIR
mkdir -p $KD__DAILY
mkdir -p $KD_WEEKLY
my_prex_or_die "mpirun python ../kd.py -i $INPUTDIR -m $MASKFILE -o $KD__DAILY -l ave*.nc"
my_prex_or_die "mpirun python ../weekly_averager.py -i $KD__DAILY -o $KD_WEEKLY -m $MASKFILE -v kd490 -t thursday"


RRS__DAILY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/RRS_DAILY/${YEAR}
RRS_WEEKLY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}

mkdir -p $RRS__DAILY
mkdir -p $RRS_WEEKLY
my_prex_or_die "mpirun python ../rrs.py -i $INPUTDIR -m $MASKFILE -o $RRS__DAILY -l ave*.nc"

for var in RRS412 RRS443 RRS490 RRS510 RRS555 RRS670; do
    my_prex_or_die "mpirun python ../weekly_averager.py --inputdir ${RRS__DAILY} --maskfile ${MASKFILE} --outdir ${RRS_WEEKLY} --timeaverage thursday --var ${var}"
done


my_prex_or_die "mpirun python ../bottom.py -i $INPUTDIR -o $BOTTOMDIR -m $MASKFILE -s ave*nc"
my_prex_or_die "mpirun python ../surf.py   -i $INPUTDIR -o $SURF__DIR -m $MASKFILE -s ave*nc"

OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/bottom/
TMPS=$OUTDIR/TMPS/${YEAR}
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc  -i $BOTTOMDIR -f Eu_0475 -a $BOTTOMDIR -d VarDescriptor_3.xml -o $OUTDIR -t $TMPS  -s "
rm -rf $TMPS
my_prex_or_die_with_tries "mpirun -np 100 python ../compact_profiles.py -i $OUTDIR/STAT_PROFILES/ -o $OUTDIR/STAT_PROFILES/"

OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/surf/
TMPS=$OUTDIR/TMPS/${YEAR}
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc  -i $SURF__DIR -f Eu_0475 -a $SURF__DIR -d VarDescriptor_3.xml -o $OUTDIR -t $TMPS  -s "
rm -rf $TMPS
my_prex_or_die_with_tries "mpirun -np 100 python ../compact_profiles.py -i $OUTDIR/STAT_PROFILES/ -o $OUTDIR/STAT_PROFILES/"

# cleaning setup 
INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}
mkdir -p $INPUTDIR/tosave
cd $INPUTDIR
for nanom in 375 400 425 475 500; do
   my_prex "mv ave.*.Es_0${nanom}.nc tosave/ "
   my_prex "mv ave.*.Ed_0${nanom}.nc tosave/ "
   my_prex "mv ave.*.Eu_0${nanom}.nc tosave/ "
done

###### Sat Validation ############

# SAT_CHLWEEKLY_DIR and SAT_VALID_DIR come from config.sh
INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
SAT_DIR=$SAT_CHLWEEKLY_DIR
LAYER=10

mkdir -p $SAT_VALID_DIR
YEAR2=$(( YEAR + 1 ))
PERIOD="-t ${YEAR}0101 -e ${YEAR2}0101"
command="mpirun python $BITSEA/src/bitsea/validation/deliverables/ScMYvalidation_plan.py"
for VAR in   P_l  P1l    P2l    P3l    P4l; do
   my_prex_or_die "$command -s $SAT_DIR -i $INPUTDIR -l $LAYER -o $SAT_VALID_DIR -c coast,open_sea $PERIOD -v $VAR -m $MASKFILE"
done

SAT_DIR=$SAT_KD_WEEKLY_DIR
for var in kd490 ; do
   my_prex_or_die "$command -s $SAT_DIR -i $INPUTDIR -l $LAYER -o $SAT_VALID_DIR -c coast,open_sea $PERIOD -v $VAR -m $MASKFILE"
done

SAT_DIR=$SAT_RRSWEEKLY_DIR
for VAR in RRS412 RRS443 RRS490 RRS510 RRS555 RRS670; do
   my_prex_or_die "$command -s $SAT_DIR -i $INPUTDIR -l 0 -o $SAT_VALID_DIR -c coast,open_sea $PERIOD -v $VAR -m $MASKFILE"
done


## COMPRESSION ##

cd $SLURM_SUBMIT_DIR/archive

INPUTDIR=$KD__DAILY
   TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v kd490"

INPUTDIR=$RRS__DAILY
   TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v RRS490"


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v N1p"


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}/tosave
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}
my_prex_or_die "./lossy_tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v Ed_0250 -s 5"

INPUTDIR=$BOTTOMDIR
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}/bottom/
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v Ed_0250"

INPUTDIR=$SURF__DIR
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}/surf/
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v Ed_0250"


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS_tar
my_prex_or_die "./tar_rstdir.sh -i $INPUTDIR -o $TARDIR -n 120"

