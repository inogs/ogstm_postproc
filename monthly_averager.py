import argparse
from bitsea.utilities.argparse_types import existing_file_path, existing_dir_path
def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates monthly averaged files
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = existing_dir_path,
                                required = True,
                                help = ''' '''

                                )

    parser.add_argument(   '--maskfile', '-m',
                                type = existing_file_path,
                                required = True,
                                help = ''' mask filename .'''
                                )

    parser.add_argument(   '--outdir', '-o',
                                type = existing_dir_path,
                                required = True,
                                help = ''' output directory'''
                                )
    parser.add_argument(   '--varlistfile', '-v',
                                type = existing_file_path,
                                required = True,
                                help = ''' file containing list of variables to average'''
                                )
    return parser.parse_args()


args = argument()

from bitsea.commons.Timelist import TimeList
from bitsea.commons.mask import Mask
from bitsea.commons.time_averagers import TimeAverager3D, TimeAverager2D
import netCDF4 as NC
from bitsea.commons import netcdf4
from bitsea.commons.utils import file2stringlist
import numpy as np


try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


INPUTDIR=args.inputdir
OUTPUTDIR=args.outdir

try:
    TheMask=Mask.from_file(args.maskfile)
except AttributeError:
    TheMask=Mask(args.maskfile)



VARLIST=file2stringlist(args.varlistfile)
var = VARLIST[0]
nvars=len(VARLIST)
TL=TimeList.fromfilenames(None, INPUTDIR, "ave*.nc" , filtervar=var)
MONTHLY_REQS = TL.getMonthlist()
nOutTimes = len(MONTHLY_REQS)

PROCESSES = np.arange(nOutTimes * nvars)
for ip in PROCESSES[rank::nranks]:
    (ireq, ivar) = divmod(ip,nvars)
    var     = VARLIST[ivar]
    req     = MONTHLY_REQS[ireq]

#for req in MONTHLY_REQS:
    indexes,weights=TL.select(req)

    inputvar=var
    #if var=='pH': inputvar='PH'

    outfile = OUTPUTDIR / f"ave.{req.string}01-00:00:00.{var}.nc"
    print(outfile,flush=True)
    filelist=[]
    for k in indexes:
        t = TL.Timelist[k]
        filename = INPUTDIR / f"ave.{t.strftime('%Y%m%d-%H:%M:%S')}.{inputvar}.nc"
        filelist.append(filename)
    if netcdf4.dimfile(filename, var)==3:
        M3d = TimeAverager3D(filelist, weights, inputvar, TheMask)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask,compression=True)
    else:
        M2d = TimeAverager2D(filelist, weights, inputvar, TheMask)
        netcdf4.write_2d_file(M2d, var, outfile, TheMask,compression=True)
