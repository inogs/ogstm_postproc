import argparse
from utilities.argparse_types import (existing_dir_path,
                                      path_inside_an_existing_dir)

def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates a single pkl file, containing the overall time series,
    for every variable in STAT_PROFILES.
    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = existing_dir_path,
                                required = True,
                                help = '/some/path/with/STAT_PROFILES')

    parser.add_argument(   '--outdir', '-o',
                                type = path_inside_an_existing_dir,
                                required = True,
                                help = 'Output directory'
                                )

    return parser.parse_args()


args = argument()


import numpy as np
import netCDF4
import pickle
from maskload import COASTNESS_LIST, SUBlist, DEPTHlist, nav_lev
try:
    from mpi4py import MPI
except ImportError:
    pass

from basins import V2
from commons.Timelist import TimeInterval, TimeList
from utilities.mpi_serial_interface import get_mpi_communicator

COMM = get_mpi_communicator()

INPUTDIR = args.inputdir
OUTDIR = args.outdir

OUTDIR.mkdir(exist_ok=True)


TI = TimeInterval("1900", "2150", "%Y")
TL = TimeList.fromfilenames(TI, INPUTDIR, "ave*nc")

nFrames = TL.nTimes

DEFAULT_COASTNESS_LIST = tuple(COASTNESS_LIST)
DEFAULT_SUBlist = tuple(SUBlist)
DEFAULT_DEPTHlist = tuple(DEPTHlist)


def get_info(filename):
    with netCDF4.Dataset(filename, 'r') as D:
        VARLIST = [str(v) for v in D.variables]
        first_var = VARLIST[0]
        VarObj = D.variables[first_var]
        nSub, nCoast, jpk, nStat = VarObj.shape
    return VARLIST, nSub, nCoast, jpk, nStat


FrameDesc   =""
SubDescr    =""
CoastDescr  =""
DepthDescr  =""
StatDescr   = "Mean, Std, min, p05, p25, p50, p75, p95, max"

for i in TL.filelist             : FrameDesc  +=str(i).split('.')[1] + ", "
for i in DEFAULT_SUBlist         : SubDescr   +=str(i)               + ", "
for i in DEFAULT_COASTNESS_LIST  : CoastDescr +=str(i)               + ", "
for i in DEFAULT_DEPTHlist       : DepthDescr +=str(i)               + ", "


VARLIST, nSub, nCoast, jpk, nStat = get_info(TL.filelist[0])

for var in VARLIST[COMM.Get_rank()::COMM.size]:
    outfile = OUTDIR / (var + ".pkl")
    timeseries_shape = (nFrames, nSub, nCoast, jpk, nStat)
    TIMESERIES = np.ma.zeros(timeseries_shape, dtype=np.float32)

    for iFrame, filename in enumerate(TL.filelist):
        with netCDF4.Dataset(filename, 'r') as f:
            A = f.variables[var][:]
        A[A==0]=np.nan
        A[A>=1.e+19]=np.nan
        TIMESERIES[iFrame] = A

    L = [TIMESERIES,TL]
    fid = open(outfile,"wb")
    pickle.dump(L, fid)
    fid.close()
    with netCDF4.Dataset(OUTDIR / (var + ".nc"), "w") as ncOUT:
        ncOUT.createDimension('nFrames',nFrames)
        ncOUT.createDimension('nSub',   nSub)
        ncOUT.createDimension('nCoast',nCoast)
        ncOUT.createDimension('depth', jpk)
        ncOUT.createDimension('nStat',nStat)

        ncvar = ncOUT.createVariable(var,'f',('nFrames','nSub','nCoast','depth', 'nStat'))
        ncvar[:] = TIMESERIES

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
