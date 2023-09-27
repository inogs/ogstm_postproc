import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Calculates 2d metrics on daily BGC


    Provided metrics:
    - dcm
    - phosphocline
    - nitracline1
    - nitracline2
    - averages on 0-200m of: ppn, N1p, N3n, P_l

    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = '/gpfs/work/OGS_prod_0/OPA/V5C/devel/wrkdir/2/MODEL/FORCINGS/')
    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = '/some/path/')
    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                required = True,
                                help = 'meshmask.nc')

    return parser.parse_args()

args = argument()

from commons.mask import Mask
from commons.dataextractor import DataExtractor
import numpy as np
from commons.Timelist import TimeList
from commons.utils import addsep
from surf import surfaces
from commons.layer import Layer
from layer_integral.mapbuilder import MapBuilder
from commons import netcdf4

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1

INPUTDIR=addsep(args.inputdir)
OUTPUTDIR=addsep(args.outdir)
TheMask=Mask(args.maskfile)


jpk, jpj, jpi = TheMask.shape
TL=TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar='P_l')
nFrames=TL.nTimes
layer200 = Layer(0,200)

FRAMES=range(nFrames)

for iframe in FRAMES[rank::nranks]:
    timestr = TL.Timelist[iframe].strftime("%Y%m%d-%H:%M:%S")
    print(timestr, flush=True)
    file_P_l=INPUTDIR + "ave." + timestr + ".P_l.nc"
    file_N1p=INPUTDIR + "ave." + timestr + ".N1p.nc"
    file_N3n=INPUTDIR + "ave." + timestr + ".N3n.nc"
    file_O2o=INPUTDIR + "ave." + timestr + ".O2o.nc"
    file_ppn=INPUTDIR + "ave." + timestr + ".ppn.nc"

    P_l=DataExtractor(TheMask,file_P_l,"P_l")
    N1p=DataExtractor(TheMask,file_N1p,"N1p")
    N3n=DataExtractor(TheMask,file_N3n,"N3n")
    O2o=DataExtractor(TheMask,file_O2o,"O2o")
    ppn=DataExtractor(TheMask,file_ppn,"ppn")

    DCM,CM,_,_         = surfaces.DCM2(         P_l.values, TheMask)
    WLB,_,_,_          = surfaces.MWB2(         P_l.values, TheMask)
    DOM,OM,_,_         = surfaces.DCM2(         O2o.values, TheMask)
    Phosphocline,_,_,_ = surfaces.NUTRCL_dz_max(N1p.values, TheMask)
    Nitracline_1,_,_,_ = surfaces.NUTRCL_dz_max(N3n.values, TheMask)
    Nitracline_2,_     = surfaces.NITRCL(       N3n.values, TheMask, 2.0)

    Int_ppn = MapBuilder.get_layer_average(ppn, layer200)
    Int_P_l = MapBuilder.get_layer_average(P_l, layer200)
    Int_N3n = MapBuilder.get_layer_average(N3n, layer200)
    Int_N1p = MapBuilder.get_layer_average(N1p, layer200)
    Int_O2o = MapBuilder.get_layer_average(O2o, layer200)

    outfile=OUTPUTDIR + "metrics." + timestr + ".nc"
    netcdf4.write_2d_file(DCM,'dcm', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(CM , 'cm', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(WLB,'WLB', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(DOM,'DOM', outfile, TheMask, compression=True)
    netcdf4.write_2d_file( OM, 'OM', outfile, TheMask, compression=True)

    netcdf4.write_2d_file(Phosphocline,'phosphocline', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Nitracline_1,'nitracline', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Nitracline_2,'nitracline_th2', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Int_P_l,'P_l', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Int_N3n,'N3n', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Int_N1p,'N1p', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Int_O2o,'O2o', outfile, TheMask, compression=True)
    netcdf4.write_2d_file(Int_ppn,'ppn', outfile, TheMask, compression=True)
