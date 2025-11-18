import argparse
from bitsea.utilities.argparse_types import (existing_dir_path,
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


from collections import OrderedDict
import numpy as np
import netCDF4
import pickle
from maskload import COASTNESS_LIST, SUBlist, DEPTHlist, nav_lev
try:
    from mpi4py import MPI
except ImportError:
    pass

from bitsea.commons.Timelist import TimeInterval, TimeList
from bitsea.utilities.mpi_serial_interface import get_mpi_communicator

COMM = get_mpi_communicator()
FILL_VALUE = np.nan


INPUTDIR = args.inputdir
OUTDIR = args.outdir

OUTDIR.mkdir(exist_ok=True)


TI = TimeInterval("1900", "2150", "%Y")
TL = TimeList.fromfilenames(TI, INPUTDIR, "ave*nc")

nFrames = TL.nTimes

DEFAULT_COASTNESS_LIST = tuple(COASTNESS_LIST)
DEFAULT_SUBlist = tuple(SUBlist)
DEFAULT_DEPTHlist = tuple(DEPTHlist)
DEFAULT_StatDescr   = "Mean, Std, min, p05, p25, p50, p75, p95, max"


def get_info(filename):
    with netCDF4.Dataset(filename, 'r') as D:
        VARLIST = [str(v) for v in D.variables]
        first_var = VARLIST[0]
        VarObj = D.variables[first_var]
        nSub, nCoast, jpk, nStat = VarObj.shape

        attributes = OrderedDict()
        if 'sub___list' in D.ncattrs():
            attributes['sub___list'] = D.sub___list
        else:
            sub_list = ', '.join([str(basin) for basin in DEFAULT_SUBlist])
            attributes['sub___list'] = sub_list

        if 'coast_list' in D.ncattrs():
            attributes['coast_list'] = D.coast_list
        else:
            attributes['coast_list'] = ', '.join(DEFAULT_COASTNESS_LIST)

        if 'depth_list' in D.ncattrs():
            attributes['depth_list'] = D.depth_list
        else:
            attributes['depth_list'] = ', '.join(DEFAULT_DEPTHlist)

        if "stat__list" in D.ncattrs():
            attributes['stat__list'] = D.stat__list
        else:
            attributes['stat__list'] = DEFAULT_StatDescr

    return VARLIST, nSub, nCoast, jpk, nStat, attributes


FrameDesc = ""
for i in TL.filelist:
    FrameDesc += str(i).split('.')[1] + ", "


VARLIST, nSub, nCoast, jpk, nStat, file_attributes = get_info(TL.filelist[0])

for var in VARLIST[COMM.Get_rank()::COMM.size]:
    outfile = OUTDIR / (var + ".pkl")
    timeseries_shape = (nFrames, nSub, nCoast, jpk, nStat)
    TIMESERIES = np.ma.zeros(timeseries_shape, dtype=np.float32)

    for iFrame, filename in enumerate(TL.filelist):
        with netCDF4.Dataset(filename, 'r') as f:
            if var in f.variables.keys():
                A = f.variables[var][:]
            else:
                msg=f"{var} not present in {str(filename)}"
                #print(msg)
                raise ValueError( f"{var} not present in {str(filename)}" )
        A[A == 0] = FILL_VALUE
        A[A >= 1.e+19] = FILL_VALUE
        TIMESERIES[iFrame] = A

    L = [TIMESERIES, TL]
    with open(outfile, "wb") as fid:
        pickle.dump(L, fid)

    time_array = TL.get_datetime_array(resolution='s')

    with netCDF4.Dataset(OUTDIR / (var + ".nc"), "w") as ncOUT:
        ncOUT.createDimension('nFrames', nFrames)
        ncOUT.createDimension('nSub',   nSub)
        ncOUT.createDimension('nCoast', nCoast)
        ncOUT.createDimension('depth', jpk)
        ncOUT.createDimension('nStat', nStat)

        ncvar = ncOUT.createVariable(
            var,
            'f',
            ('nFrames', 'nSub', 'nCoast', 'depth', 'nStat'),
            fill_value=FILL_VALUE
        )
        ncvar[:] = TIMESERIES

        ncvar = ncOUT.createVariable('depth', 'f', ('depth',))
        setattr(ncvar, 'units', 'meters')
        setattr(ncvar, 'positive', 'down')
        setattr(
            ncvar,
            'actual_range',
            '{}, {}'.format(
                np.float32(np.ma.min(nav_lev)),
                np.float32(np.ma.max(nav_lev))
            )
        )
        ncvar[:] = nav_lev

        time_var = ncOUT.createVariable('time', np.int64, ('nFrames',))
        time_var.units = 'seconds since 1970-01-01 00:00:00'
        time_var[:] = np.asarray(time_array-np.datetime64('1970-01-01','s'), dtype=np.int64)

        setattr(ncOUT, "frame_list", FrameDesc)
        for attribute, attribute_value in file_attributes.items():
            setattr(ncOUT, attribute, attribute_value)
