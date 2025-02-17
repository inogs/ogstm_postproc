#! /bin/bash

REF_DIR=/g100_scratch/userexternal/camadio0/Neccton_hindcast1999_2022/wrkdir/MODEL

ln -fs $REF_DIR/meshmask.nc

mkdir -p AVE_FREQ_1 AVE_FREQ_2 AVE_FREQ_3 RESTARTS

cd AVE_FREQ_2
#for I in $( \ls $REF_DIR/AVE_FREQ_2 ) ; do
#	ln -s $REF_DIR/AVE_FREQ_2/$I
#done

cd ../AVE_FREQ_3
for I in $( \ls $REF_DIR/AVE_FREQ_3 ) ; do
        ln -s $REF_DIR/AVE_FREQ_3/$I
done

cd ../RESTARTS
for I in $( \ls $REF_DIR/RESTARTS ) ; do
        ln -s $REF_DIR/RESTARTS/$I
done

