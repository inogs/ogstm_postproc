import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates KD based on PAR
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = ''' AVE_FREQ_1 dir'''
                                )
    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                required = True,
                                help = ''' mask filename'''
                                )

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = ''' path of the output Kd dir '''
                                )
    return parser.parse_args()


args = argument()


import numpy as np
from commons.mask import Mask
from commons.dataextractor import DataExtractor
from commons import netcdf4
from commons.Timelist import TimeList
from commons.utils import addsep

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


INPUTDIR=addsep(args.inputdir)
OUTDIR  =addsep(args.outdir)
TheMask = Mask(args.maskfile)

jpk,jpj,jpi = TheMask.shape


def load_data(var, dateobj):
    filename = "%save.%s.%s.nc" %(INPUTDIR,dateobj.strftime("%Y%m%d-%H:%M:%S"),var)
    print(filename,flush=True)
    return DataExtractor(TheMask,filename, var).values



TL = TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar="PAR")

for d in TL.Timelist[rank::nranks]:
    
    E = load_data('PAR', d)
    KD = np.ones((jpk,jpj,jpi),np.float32)* 1.e-8
    jk_lim = TheMask.getDepthIndex(500.) -2


    KD[:jk_lim,:,:] = -np.log(E[1:jk_lim+1,:,:]/E[0:jk_lim,:,:])#/TheMask.e3t[:jk_lim,:,:]
    KD[~TheMask.mask] = 1.e+20


    varname ="kd"
    outfile ="%save.%s.%s.nc" %(OUTDIR,d.strftime("%Y%m%d-%H:%M:%S"),varname)
    print(outfile)
    netcdf4.write_3d_file(KD, varname, outfile, TheMask, compression=True)

                
                
    