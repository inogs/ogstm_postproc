import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates bottom 2d files
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = ''' '''
                                )

    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                required = True,
                                help = ''' mask filename .'''
                                )

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = ''' output directory'''
                                )
    parser.add_argument(   '--var', '-v',
                                type = str,
                                required = True,
                                help = ''' model var name'''
                                )
    return parser.parse_args()


args = argument()

from commons.Timelist import TimeList
from commons.mask import Mask
from commons.dataextractor import DataExtractor
import numpy as np
from commons import netcdf4
from commons.utils import addsep
from pathlib import Path
import os

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


INPUTDIR=addsep(args.inputdir)
OUTPUTDIR=Path(args.outdir)

TheMask=Mask(args.maskfile)
jpk,jpj,jpi = TheMask.shape

var = args.var
TL=TimeList.fromfilenames(None, INPUTDIR, "ave*.nc" , filtervar=var)

bottom= TheMask.bathymetry_in_cells()
mask0 = TheMask.mask_at_level(0)

def getBottom(M3d):
    M2d=np.ones((jpj,jpi),np.float32)*1.e+20
    for ji in range(jpi):
        for jj in range(jpj):
            if mask0[jj,ji]:
                b = bottom[jj,ji] -1
                M2d[jj,ji]=M3d[b,jj,ji]
    return M2d


for filename in TL.filelist[rank::nranks]:
    outfile= OUTPUTDIR / os.path.basename(filename)
    print(outfile, flush=True)
    M3d = DataExtractor(TheMask,filename, var).values
    M2d  = getBottom(M3d)
    netcdf4.write_2d_file(M2d, var, outfile, TheMask, compression=True)



