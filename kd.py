import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates kd380, kd412 and kd490 files
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = ''' AVE_FREQ_3 dir'''
                                )
    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                required = True,
                                help = ''' mask filename'''
                                )
    parser.add_argument(   '--avelist',"-l",
                                type = str,
                                required = True,
                                help = 'ave.2019*.nc, they configure the date list')
    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = ''' path of the output Kd dir '''
                                )
    return parser.parse_args()


args = argument()


import numpy as np
from bitsea.commons.utils import data_for_linear_interp
from datetime import datetime
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
TheMask = Mask(args.maskfile)

jpk,jpj,jpi = TheMask.shape
mask0 = TheMask.mask_at_level(0)

opt_mask = np.zeros((jpk,jpj,jpi),bool)
bottom= TheMask.bathymetry_in_cells()
for ji in range(jpi):
    for jj in range(jpj):
        if mask0[jj,ji]:
            b = bottom[jj,ji]
            opt_mask[:b+1,jj,ji] = True



freq_nanom = [250, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625,
       650, 675, 700, 725, 775, 850, 950, 1050, 1150, 1250, 1350, 1450, 1550, 1650,
       1750, 1900, 2200, 2900, 3700]

absorption=[0.6112, 0.0218, 0.0081, 0.0057, 0.0047,0.0049,0.0085,0.0117,0.0215]#morel


def load_data(prefix,index_freq, dateobj):
    var = "%s_%04d" %(prefix, freq_nanom[index_freq])
    filename = "%save.%s.%s.nc" %(INPUTDIR,dateobj.strftime("%Y%m%d-%H:%M:%S"),var)
    print(filename,flush=True)
    return DataExtractor(TheMask,filename, var).values


def get_E(dateobj, interp_data):
    freq_before, freq_after, w = interp_data
    E_before = load_data("Ed", freq_before, dateobj)
    E_after  = load_data("Ed", freq_after , dateobj)
    Ed = E_before*(1-w) + w*E_after
    Ed[~opt_mask] = 1.e+20
    
    E_before = load_data("Es", freq_before, dateobj)
    E_after  = load_data("Es", freq_after , dateobj)
    Es = E_before*(1-w) + w*E_after    
    Es[~opt_mask] = 1.e+20
    return Ed + Es

def freq_absorption(interp_data):
    freq_before, freq_after, w = interp_data
    return absorption[freq_before]*(1-w) + absorption[freq_after]*w

TL = TimeList.fromfilenames(None, INPUTDIR, args.avelist, filtervar="Ed_0500")

for d in TL.Timelist[rank::nranks]:
    for wavelengh in [380, 412, 490]:
        interp_data = data_for_linear_interp(freq_nanom,wavelengh)
        E = get_E(d, interp_data)
        KD = np.ones((jpk,jpj,jpi),np.float32) * freq_absorption(interp_data)
        jk_lim = TheMask.getDepthIndex(500.)


        KD[:jk_lim,:,:] = -np.log(E[1:jk_lim+1,:,:]/E[0:jk_lim,:,:])/TheMask.e3t[:jk_lim,:,:]
        KD[~TheMask.mask] = 1.e+20


        varname="kd%s" %wavelengh
        outfile ="%save.%s.%s.nc" %(OUTDIR,d.strftime("%Y%m%d-%H:%M:%S"),varname)
        print("rank %d dumps %s" %(rank,outfile))
        netcdf4.write_3d_file(KD, varname, outfile, TheMask, compression=True)

                
                
    