import argparse
from bitsea.utilities.argparse_types import existing_dir_path, existing_file_path
def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates bottom 2d files
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
    parser.add_argument(   '--searchstring',"-s",
                                type = str,
                                default = "ave*N1p.nc",
                                help = 'ave*.N1p.nc')
    return parser.parse_args()


args = argument()

from bitsea.commons.mask import Mask
from bitsea.commons.dataextractor import DataExtractor
import numpy as np
from bitsea.commons import netcdf4
from bitsea.utilities.mpi_serial_interface import get_mpi_communicator
import mpi4py.MPI
comm = get_mpi_communicator()
rank  = comm.Get_rank()
nranks =comm.size


INPUTDIR=args.inputdir
OUTPUTDIR=args.outdir

TheMask=Mask.from_file(args.maskfile)


filelist= tuple(INPUTDIR.glob(args.searchstring))


bottom= TheMask.bathymetry_in_cells()
mask0 = TheMask.mask_at_level(0)

def getBottom(M3d,mask0,bottom):
    jpj,jpi = mask0.shape
    M2d=np.ones((jpj,jpi),np.float32)*1.e+20
    for ji in range(jpi):
        for jj in range(jpj):
            if mask0[jj,ji]:
                b = bottom[jj,ji] -1
                M2d[jj,ji]=M3d[b,jj,ji]
    return M2d


for filename in filelist[rank::nranks]:
    outfile= OUTPUTDIR / filename.name
    print(outfile, flush=True)
    var=filename.name.rsplit(".")[2]
    M3d = DataExtractor(TheMask,filename, var).values
    M2d  = getBottom(M3d,mask0,bottom)
    netcdf4.write_2d_file(M2d, var, outfile, TheMask, compression=True)



