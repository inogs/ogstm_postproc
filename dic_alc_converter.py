import argparse


def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates O3c and O3h files from DIC and ALK files
    ''')
    parser.add_argument(   '--Maskfile_ingv', '-M',
                                type = str,
                                required = True,
                                help = 'Path of the CMCC Mask file'
                                )
    parser.add_argument(   '--maskfile','-m',
                                type = str,
                                required = True,
                                help = 'Path of the OGSTM mask file'
                                )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = 'Path of the input dir'
                                )
    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = 'Path of the output dir'
                                )
    parser.add_argument(   '--forcingsdir', '-f',
                                type = str,
                                required = True,
                                help = 'Path of the forcings dir'
                                )
    parser.add_argument(   '--starttime', '-s',
                                type = str,
                                required = True,
                                help = 'initial tyme string yyyymmdd'
                                )
    parser.add_argument(   '--endtime', '-e',
                                type = str,
                                required = True,
                                help = 'end tyme string yyyymmdd'
                                )


    return parser.parse_args()

args = argument()

from bitsea.commons.mask import Mask
import numpy as np
from bitsea.commons import density
from bitsea.commons import netcdf4
from bitsea.commons.dataextractor import DataExtractor
from bitsea.commons.Timelist import TimeInterval,TimeList
from bitsea.commons.utils import addsep

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


TheMask=Mask(args.maskfile)
IngvMask= Mask(args.Maskfile_ingv)
INDIR = addsep(args.inputdir)
OUTDIR = addsep(args.outdir)
FORCDIR = addsep(args.forcingsdir)
ST = args.starttime
ET = args.endtime

jpk, jpj, jpi = TheMask.shape
JPK, JPJ, JPI = IngvMask.shape


TI = TimeInterval(ST,ET,'%Y%m%d')

TL = TimeList.fromfilenames(TI,INDIR,'ave.*DIC.nc')

for t in TL.Timelist[rank::nranks]:
	d = t.strftime('%Y%m%d')
	filename=FORCDIR + 'T'+ d +'-12:00:00.nc'


	rho = density.get_density(filename, IngvMask)
	rho = rho[:jpk,:,JPI-jpi:]


	inputfile = INDIR + 'ave.' + d + '-12:00:00.' + 'DIC.nc'
	outfile =  OUTDIR + 'ave.' + d + '-12:00:00.' + 'O3c.nc'
	print (outfile,flush=True)

	DIC = DataExtractor(TheMask,inputfile,'DIC').values 
	O3c = rho * DIC * 12 /1000 
	O3c[~TheMask.mask] = 1.e+20
	netcdf4.write_3d_file(O3c, 'O3c', outfile, TheMask,compression=True)


	inputfile = INDIR + 'ave.' + d + '-12:00:00.' + 'ALK.nc'
	outfile  = OUTDIR + 'ave.' + d + '-12:00:00.' + 'O3h.nc'
	print (outfile)

	ALK = DataExtractor(TheMask,inputfile,'ALK').values
	O3h = rho * ALK /1000 
	O3h[~TheMask.mask] = 1.e+20
	netcdf4.write_3d_file(O3h, 'O3h', outfile, TheMask, compression=True)

	



