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
from bitsea.commons.mask import Mask
from bitsea.commons.dataextractor import DataExtractor
from bitsea.commons import netcdf4
from bitsea.commons.Timelist import TimeList
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
OUTDIR  =addsep(args.outdir)
TheMask = Mask.from_file(args.maskfile)

jpk,jpj,jpi = TheMask.shape


def load_data(var, dateobj):
    filename = "%save.%s.%s.nc" %(INPUTDIR,dateobj.strftime("%Y%m%d-%H:%M:%S"),var)
    print(filename,flush=True)
    return DataExtractor(TheMask,filename, var).values



TL = TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar="PAR")
jk_lim = TheMask.getDepthIndex(500.) -2
Bathycells = TheMask.bathymetry_in_cells()

for d in TL.Timelist[rank::nranks]:
    
    E = load_data('PAR', d)
    prev_value, new_value=100.0, 100.0
    for jk in range(jk_lim+1):
        v=E[jk,:,:]
        ii=v==0
        J,I=np.nonzero(ii)
        nzeros=len(I)
        for k in range(nzeros):
            ji=I[k]
            jj=J[k]
            m = v[jj-1:jj+2, ji-1:ji+2] # 3x3
            mask=TheMask.mask[jk,jj-1:jj+2, ji-1:ji+2]
            mask[1,1]=False
            if mask.any():
                new_value =  m[mask].mean()
                if new_value >0:
                    E[jk,jj,ji] = new_value
                else:
                    E[jk,jj,ji] = prev_value
            prev_value=new_value


    KD = np.ones((jpk,jpj,jpi),np.float32)* 1.e-8
    KD[~TheMask.mask] = 1.e+20

    for i in range(jpi):
        for j in range(jpj):
            b = min(Bathycells[j,i]-2,jk_lim)
            for k in range(b):
                KD[k,j,i] = -np.log(E[k+1,j,i]/E[k,j,i])/TheMask.e3t[k,j,i]
    #KD[:jk_lim,:,:] = -np.log(E[1:jk_lim+1,:,:]/E[0:jk_lim,:,:])/TheMask.e3t[:jk_lim,:,:]

    varname ="kd"
    outfile ="%save.%s.%s.nc" %(OUTDIR,d.strftime("%Y%m%d-%H:%M:%S"),varname)
    print(outfile)
    netcdf4.write_3d_file(KD, varname, outfile, TheMask, compression=True)

                
                
    