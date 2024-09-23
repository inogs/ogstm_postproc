import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    For a given variable, dumps a file called
    PROF_18aree_' + varname + '.nc
    ''')
    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                default = '/pico/home/usera07ogs/a07ogs00/OPA/V4/etc/static-data/MED1672_cut/MASK/meshmask.nc')

    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required=True,
                                help = '/pico/scratch/userexternal/gbolzon0/RA_CARBO/RA_02/wrkdir/POSTPROC/output/AVE_FREQ_2/4x4/STAT_PROFILES/')
    parser.add_argument(   '--var', '-v',
                                type = str,
                                required=True,
                                help = 'ogstm varname')
 
    return parser.parse_args()

args = argument()
import scipy.io.netcdf as NC
import numpy as np
import glob
from bitsea.commons.mask import Mask
from bitsea.commons.utils import addsep


TheMask=Mask(args.maskfile)

INPUTDIR=addsep(args.inputdir)
varname = args.var

FILELIST=glob.glob(INPUTDIR+"*nc")

nSub=18
iStat=0 #media
jpk,_,_ = TheMask.shape

nFrames = len(FILELIST)
VARiz = np.zeros((nFrames,jpk,nSub),dtype=np.float32)

for iFrame, filename in enumerate(FILELIST):
    ncIN = NC.netcdf_file(filename,'r')
    icoast= ncIN.coast_list.rsplit(", ").index('open_sea')
    A=ncIN.variables[varname].data.copy()
    ncIN.close()
    for iSub in range(nSub):
        for jk in range(jpk):
            VARiz[iFrame,jk,iSub] = A[iSub,icoast,jk,iStat]


ii=VARiz==0; 
VARiz[ii] = 1.e+20

ncOUT = NC.netcdf_file('PROF_18aree_' + varname + '.nc','w')
ncOUT.createDimension('depth',jpk)
ncOUT.createDimension('area',nSub)
ncOUT.createDimension('time',nFrames)

depth = ncOUT.createVariable('depth','f',('depth',))
depth[:] = TheMask.zlevels
setattr(depth,'units','depth of center of the cells: nav_lev')

data = ncOUT.createVariable(varname,'f',('time','depth','area'))
data[:]=VARiz
setattr(data,'missing_value',1.e+20)
setattr(data,'actual_range', '%g , %g' %(VARiz[~ii].min(), VARiz[~ii].max()))
ncOUT.close()


