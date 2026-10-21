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

from bitsea.commons.Timelist import TimeList, TimeInterval
from bitsea.commons.mask import Mask
from bitsea.commons.time_averagers import TimeAverager3D, TimeAverager2D
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

TheMask=Mask.from_file(args.maskfile)
var = args.var

TI= TimeInterval('1999','2020', '%Y')
VARLIST=file2stringlist(args.varlistfile)
var = VARLIST[0]
nvars=len(VARLIST)
TL=TimeList.fromfilenames(None, INPUTDIR, "ave*.nc", filtervar=var)
YEARLY_REQS=TL.getYearlist()
nOutTimes = len(YEARLY_REQS)

PROCESSES = np.arange(nOutTimes * nvars)
for ip in PROCESSES[rank::nranks]:
    (ireq, ivar) = divmod(ip,nvars)
    var     = VARLIST[ivar]
    req     = YEARLY_REQS[ireq]
#for req in MONTHLY_REQS:    
    indexes,weights=TL.select(req)

    if len(indexes)==0: continue
    inputvar=var

    outfile = OUTPUTDIR / f"ave.{req.string}01-00:00:00.{var}.nc"
    print(outfile,flush=True)
    filelist=[]
    for k in indexes:
        t = TL.Timelist[k]
        filename = INPUTDIR / f"ave.{t.strftime('%Y%m%d-%H:%M:%S')}.{inputvar}.nc"
        filelist.append(filename)
    if netcdf4.dimfile(filename, var)==3:
        M3d = TimeAverager3D(filelist, weights, inputvar, TheMask, compression=True)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask)
    else:
        M2d = TimeAverager2D(filelist, weights, inputvar, TheMask, compression=True)
        netcdf4.write_2d_file(M2d, var, outfile, TheMask)
