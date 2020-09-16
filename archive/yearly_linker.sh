#! /bin/bash

# creates yearly directories in $OUTDIR

INPUTDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_11/wrkdir/MODEL/AVE_FREQ_1
OUTDIR=/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_11/wrkdir/POSTPROC/ARCHIVE
mkdir -p $OUTDIR

for year in `seq 1999 2002 `; do 
   mkdir $OUTDIR/$year
   cd $OUTDIR/$year
   for I in  $INPUTDIR/ave.${year}* ; do
      ln -s $I
   done 
done

