#! /bin/bash

#SBATCH --job-name=POST
#SBATCH -N5
#SBATCH --ntasks-per-node=24
#SBATCH --time=02:30:00
#SBATCH --mem=300gb
#SBATCH --account=OGS_devC
#SBATCH --partition=g100_meteo_prod
#SBATCH --qos=qos_meteo


usage() {
echo "SYNOPSYS"
echo "sbatch job.POST.my.slurm -y YEAR"
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

cd $SLURM_SUBMIT_DIR

unset I_MPI_PMI_LIBRARY
export UCX_TLS=ib
export SLURM_PMIX_DIRECT_CONN_UCX=false


export    MASKFILE=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/meshmask.nc
export  KCOASTFILE=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/mapser.npy

export PATH=$PATH:..

####### moving in year/ directories ################
MODEL_AVEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/
cd $MODEL_AVEDIR

mkdir -p AVE_FREQ_1/${YEAR} AVE_FREQ_2/${YEAR} AVE_FREQ_3/${YEAR} RESTARTS/${YEAR}

cd $MODEL_AVEDIR/AVE_FREQ_1
my_prex "mv ave.${YEAR}*.nc ${YEAR}/ "

cd $MODEL_AVEDIR/AVE_FREQ_2
my_prex "mv ave.${YEAR}*.nc ${YEAR}/ "
rm -f ave.${YEAR}.nc.bkp

cd $MODEL_AVEDIR/AVE_FREQ_3
my_prex "mv ave.${YEAR}*.nc ${YEAR}/"

cd $MODEL_AVEDIR/RESTARTS
my_prex "mv RST.${YEAR}*.nc ${YEAR}/"

########  HIGH FREQUENCY ######################################################

cd $SLURM_SUBMIT_DIR

MODEL_AVEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/${YEAR}

my_prex_or_die_with_tries "mpirun -np 120 python ../var_aggregator.py -l ave*N1p.nc -i $MODEL_AVEDIR -d VarDescriptor_1.xml -t $MODEL_AVEDIR -m $MASKFILE"
OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_1/metrics_2d
mkdir -p $OUTDIR
my_prex_or_die_with_tries "mpirun -np 120 python ../metrics_2d.py -i $MODEL_AVEDIR -m $MASKFILE -o $OUTDIR"

########## Profiling model in observation positions ##############

  TMPS=$BASEDIR/TMPS
# floats
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc  -i $MODEL_AVEDIR -f O2o -a $MODEL_AVEDIR -d VarDescriptorB.xml -o $BASEDIR -t $TMPS -p $BASEDIR/PUNTI "
my_prex_or_die "rm -rf $TMPS"


# Emodnet
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc  -i $MODEL_AVEDIR -f O2o -a $MODEL_AVEDIR -d VarDescriptorB.xml -o $EBASEDIR -t $TMPS -p $EBASEDIR/PUNTI "
my_prex_or_die "rm -rf $TMPS"

########## Profiling in float positions ##############

export BASINS=V2
OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/${BASINS}/AVE_FREQ_1/
TMPS=$OUTDIR/TMPS
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc     -i $MODEL_AVEDIR -f N1p -a $MODEL_AVEDIR -d VarDescriptor_1.xml -o $OUTDIR -t $TMPS  -s "
my_prex_or_die "rm -rf $TMPS"
my_prex_or_die_with_tries "mpirun -np 16 python ../compact_profiles.py -i $OUTDIR/STAT_PROFILES/ -o $OUTDIR/STAT_PROFILES/"



########  LOW FREQUENCY ######################################################

cd $SLURM_SUBMIT_DIR

MODEL_AVEDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
      OUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_2/

        TMPS=$OUTDIR/TMPS
  CHLSUP_DIR=$OUTDIR/CHL_SUP

my_prex_or_die_with_tries "mpirun -np 120 python ../var_aggregator.py -l ave*N1p.nc -i $MODEL_AVEDIR -d VarDescriptor_2.xml -t $MODEL_AVEDIR -c $CHLSUP_DIR -m $MASKFILE"
export BASINS=V2
my_prex_or_die_with_tries "mpirun python ../aveScan.py  -l ave*nc     -i $MODEL_AVEDIR -f N1p -a $MODEL_AVEDIR -d VarDescriptor_2.xml -o $OUTDIR -t $TMPS  -s "

my_prex_or_die "rm -rf $TMPS"

my_prex_or_die_with_tries "mpirun -np 16 python ../compact_profiles.py -i $OUTDIR/STAT_PROFILES/ -o $OUTDIR/STAT_PROFILES/"

################## end of integrals/profiles stuff  ##############

################ Kd  #########################

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}
KD__DAILY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/KD_DAILY
KD_WEEKLY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/KD_WEEKLY

mkdir -p $KD__DAILY
mkdir -p $KD_WEEKLY
my_prex_or_die "mpirun python ../kd.py -i $INPUTDIR -m $MASKFILE -o $KD__DAILY -l ave*.nc"
my_prex_or_die "mpirun python ../weekly_averager.py -i $KD__DAILY -o $KD_WEEKLY -m $MASKFILE -v kd490 -t monday"


RRS__DAILY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/RRS_DAILY
RRS_WEEKLY=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/AVE_FREQ_3/RRS_WEEKLY

mkdir -p $RRS__DAILY
mkdir -p $RRS_WEEKLY
my_prex_or_die "mpirun python ../rrs.py -i $INPUTDIR -m $MASKFILE -o $RRS__DAILY -l ave*.nc"

for var in RRS412 RRS443 RRS490 RRS510 RRS555 RRS670; do
    my_prex_or_die "python ../weekly_averager.py --inputdir ${RRS__DAILY} --maskfile ${MASKFILE} --outdir ${RRS_WEEKLY} --timeaverage thursday --var ${var}"
done

############     yearly averages   ###########################

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
OUTPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/POSTPROC/output/YEARLY
mkdir -p $OUTPUTDIR

for var in ppn P_l N3n N1p ALK DIC O2o; do
    my_prex_or_die "python ../yearly_averager.py -i $INPUTDIR -o $OUTPUTDIR -v $var -m $MASKFILE"
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

## COMPRESSION ##


cd $SLURM_SUBMIT_DIR/../archive
INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_1_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v N1p"
cd $KD__DAILY
my_prex_or_die "tar -cf $TARDIR/kd490.tar ave.${YEAR}*kd490.nc"

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_2_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v N1p"


INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/AVE_FREQ_3_tar/${YEAR}
my_prex_or_die "./tar_avedir.sh -i $INPUTDIR -o $TARDIR -n 120 -v Ed_0250"

INPUTDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS/${YEAR}
  TARDIR=$CINECA_SCRATCH/$OPA_HOME/wrkdir/MODEL/RESTARTS_tar/${YEAR}
my_prex_or_die "./tar_rstdir.sh -i $INPUTDIR -o $TARDIR -n 120"



