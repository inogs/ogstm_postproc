#!/usr/bin/env python
# Author: Giorgio Bolzon <gbolzon@ogs.trieste.it>
# Script to generate profiles of model files in
# the same time and locations where instruments
# such as bioFloats, mooring or vessels have been found.
# When imported, this scripts only defines settings for matchup generation.

from bitsea.static.Nutrients_reader import NutrientsReader

from bitsea.instruments.matchup_manager import Matchup_Manager
from bitsea.commons.time_interval import TimeInterval
from bitsea.commons.Timelist import TimeList
from bitsea.basins.region import Rectangle

INPUTDIR='@@INPUTDIR@@'

# output directory, where aveScan.py will be run.

BASEDIR='@@BASEDIR@@'


DATESTART = '@@YEAR1@@0101'
DATE__END = '@@YEAR2@@0101'

T_INT = TimeInterval(DATESTART,DATE__END, '%Y%m%d')
TL = TimeList.fromfilenames(T_INT, INPUTDIR,"ave*.nc",filtervar="N1p")
N = NutrientsReader()
ALL_PROFILES = N.Selector(None,T_INT, Rectangle(-6,36,30,46))


vardescriptorfile="VarDescriptorB.xml"

#This previous part will be imported in matchups setup.

# The following part, the profiler, is executed once and for all.
# It might take some time, depending on length of simulation or size of files.
if __name__ == '__main__':
    # Here instruments time and positions are read as well as model times
    M = Matchup_Manager(ALL_PROFILES,TL,BASEDIR)

    profilerscript = BASEDIR + 'jobProfiler.sh'
    M.writefiles_for_profiling(vardescriptorfile, profilerscript, aggregatedir=INPUTDIR) # preparation of data for aveScan

