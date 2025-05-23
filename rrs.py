import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates rrs files
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
TheMask = Mask.from_file(args.maskfile)

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
    return DataExtractor(TheMask,filename, var, dimvar=2).values


def get_RRS(dateobj, interp_data):
    freq_before, freq_after, w = interp_data
    E_before = load_data("Ed", freq_before, dateobj)
    E_after  = load_data("Ed", freq_after , dateobj)
    Ed = E_before*(1-w) + w*E_after
    Ed[~mask0] = 1.e+20
#   Ed[~opt_mask] = 1.e+20
    
    E_before = load_data("Es", freq_before, dateobj)
    E_after  = load_data("Es", freq_after , dateobj)
    Es = E_before*(1-w) + w*E_after    
    Es[~mask0] = 1.e+20
#   Es[~opt_mask] = 1.e+20

    E_before = load_data("Eu", freq_before, dateobj)
    E_after  = load_data("Eu", freq_after , dateobj)
    Eu = E_before*(1-w) + w*E_after    
    Eu[~mask0] = 1.e+20
#   Eu[~opt_mask] = 1.e+20

    return Eu/(Ed + Es)

def freq_absorption(interp_data):
    freq_before, freq_after, w = interp_data
    return absorption[freq_before]*(1-w) + absorption[freq_after]*w

TL = TimeList.fromfilenames(None, INPUTDIR, args.avelist, filtervar="Ed_0500")

for d in TL.Timelist[rank::nranks]:

    Q = 4.0 # To be substituted by time/space dependent formula

    for wavelengh in [412, 443, 490, 510, 555, 670]:

        interp_data = data_for_linear_interp(freq_nanom,wavelengh)
        RRS0m = get_RRS(d, interp_data)

#derive Rrs0p from Rrs0m using the correction by Lee et al. 2002
        T=0.52
        GammaQ=1.7
        RRS0p = T*RRS0m/(1.0-GammaQ*RRS0m)/Q
        RRS0p[~mask0] = 1.e+20

        varname="RRS%s" %wavelengh
        outfile ="%save.%s.%s.nc" %(OUTDIR,d.strftime("%Y%m%d-%H:%M:%S"),varname)
        print("rank %d dumps %s" %(rank,outfile))
        netcdf4.write_2d_file(RRS0p, varname, outfile, TheMask, compression=True)
