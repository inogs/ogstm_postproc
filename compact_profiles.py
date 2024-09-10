import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates a single pkl file, containing the overall time series, 
    for every variable in STAT_PROFILES. 
    
    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = '/some/path/with/STAT_PROFILES')

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = 'Output directory'
                                )


    return parser.parse_args()

args = argument()


from bitsea.commons.Timelist import TimeInterval,TimeList
import netCDF4
import numpy as np
from bitsea.commons import netcdf4
from maskload import *
import pickle,os
from bitsea.commons.utils import addsep
try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1




INPUTDIR=addsep(args.inputdir)
OUTDIR=addsep(args.outdir)

os.system("mkdir -p " + OUTDIR)

TI = TimeInterval("1900","2150","%Y")
TL=TimeList.fromfilenames(TI,INPUTDIR, "ave*nc")

nFrames = TL.nTimes

def get_info(filename):
    D = netCDF4.Dataset(filename)
    Ordered_DICT=D.variables
    VARLIST = [ str(v) for v in Ordered_DICT]
    var=VARLIST[0]
    VarObj= Ordered_DICT[var]
    nSub, nCoast, jpk, nStat =VarObj.shape
    D.close()
    return VARLIST, nSub, nCoast, jpk, nStat


FrameDesc   =""
SubDescr    =""
CoastDescr  =""
DepthDescr  =""
StatDescr   = "Mean, Std, min, p05, p25, p50, p75, p95, max"

for i in TL.filelist       : FrameDesc  +=str(i).split('.')[1] + ", "
for i in SUBlist           : SubDescr   +=str(i)               + ", "
for i in COASTNESS_LIST    : CoastDescr +=str(i)               + ", "
for i in DEPTHlist         : DepthDescr +=str(i)               + ", "


VARLIST, nSub, nCoast, jpk, nStat =get_info(TL.filelist[0])

for var in VARLIST[rank::nranks]:
    outfile = OUTDIR + var + ".pkl"
    TIMESERIES=np.zeros((nFrames,nSub,nCoast,jpk, nStat),dtype=np.float32)
    
    for iFrame, filename in enumerate(TL.filelist):
        A = netcdf4.readfile(filename, var)
        A[A==0]=np.nan
        A[A>=1.e+19]=np.nan
        TIMESERIES[iFrame,:,:,:,:] = A
        
    L = [TIMESERIES,TL]
    fid = open(outfile,"wb")
    pickle.dump(L, fid) 
    fid.close()
    ncOUT = netCDF4.Dataset( OUTDIR + var + ".nc","w")
    ncOUT.createDimension('nFrames',nFrames)
    ncOUT.createDimension('nSub',   nSub)
    ncOUT.createDimension('nCoast',nCoast)
    ncOUT.createDimension('depth', jpk)
    ncOUT.createDimension('nStat',nStat)
    
    ncvar=ncOUT.createVariable(var,'f',('nFrames','nSub','nCoast','depth', 'nStat'))
    ncvar[:] =TIMESERIES

    ncvar = ncOUT.createVariable('depth','f',('depth',))
    setattr(ncvar, 'units', 'meters')
    setattr(ncvar, 'positive', 'down')
    setattr(ncvar, 'actual_range', '4.9991f, 4450.068f')
    ncvar[:] = nav_lev

    setattr(ncOUT,"frame_list"  ,  FrameDesc)
    setattr(ncOUT,"sub___list"  ,  SubDescr[:-2])
    setattr(ncOUT,"coast_list"  ,CoastDescr[:-2])
    setattr(ncOUT,"depth_list"  ,DepthDescr[:-2])
    setattr(ncOUT,"stat__list"  , StatDescr    )

    ncOUT.close()
