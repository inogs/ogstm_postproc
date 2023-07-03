#! /bin/bash


export CINECA_WORK=/g100_work/OGS_devC
export OPA_HOME=Benchmark/HC

cd $CINECA_WORK/$OPA_HOME/wrkdir/POSTPROC
[[ -d bit.sea ]] || git clone git@github.com:inogs/bit.sea.git  



