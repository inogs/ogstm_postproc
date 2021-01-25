import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Create 2d files of bottom (n-1 and n-2) variables concentrations in a timelist 
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = ''' Input directory , e.g. /gss/gss_work/DRES_OGS_BiGe/Observations/TIME_RAW_DATA/ONLINE/SAT/MODIS/DAILY/ORIG/'''

                                )
    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                required = True,
                                help = ''' Output directory, e.g. /gss/gss_work/DRES_OGS_BiGe/Observations/TIME_RAW_DATA/ONLINE/SAT/MODIS/DAILY/ORIG/'''

                                )

    parser.add_argument(   '--mask', '-m',
                                type = str,
                                required = True,
                                help = ''' Name of the mesh of the meshmask used to generate files'''
                                )

    parser.add_argument(   '--starttime', '-s',
                                type = str,
                                required = True,
                                help = '''  Startime YYYY'''
                                )

    parser.add_argument(   '--endtime', '-e',
                                type = str,
                                required = True,
                                help = ''' Endtime YYYY'''

                                )
    
    parser.add_argument(   '--variable', '-v',
                                type = str,
                                required = True,
                                help = ''' Variable to extract in the input file'''

                                )

    return parser.parse_args()


args = argument()

import numpy as np
from commons.mask import Mask
from commons import netcdf4
from commons.dataextractor import DataExtractor
from commons.Timelist import TimeList,TimeInterval
from commons.utils import addsep

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
    isParallel = True
except:
    rank   = 0
    nranks = 1
    isParallel = False


inputdir   = addsep(args.inputdir)
outputdir   = addsep(args.outputdir)
mask   = args.mask
starttime = args.starttime
endtime = args.endtime
var = args.variable

#themask = Mask('/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc')
themask= Mask(mask)
bottom_indexes = themask.bathymetry_in_cells()

bottom_1 = bottom_indexes - 1
bottom_2 = bottom_indexes - 2


jpk, jpj, jpi = themask.shape

e3t_b1=np.zeros((jpj,jpi),np.float32)
e3t_b2=np.zeros((jpj,jpi),np.float32)
water = themask.mask[0,:,:]
for i in range(jpi):
    for j in range(jpj):
        b1=bottom_1[j,i]
        b2=bottom_2[j,i]
        if water[j,i]:
            e3t_b1[j,i] = themask.e3t[b1,j,i]
            e3t_b2[j,i] = themask.e3t[b2,j,i]
#var='N1p'
#inputdir='/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/AVE_FREQ_1/'
#outputdir='/gpfs/scratch/userexternal/gcoidess/TEST_VINKO_output/'
TI=TimeInterval(starttime,endtime,'%Y')
TL=TimeList.fromfilenames(TI, inputdir, '*.nc', filtervar=var)
for time in TL.Timelist[rank::nranks]:
    inputfile = inputdir+'ave.'+ time.strftime('%Y%m%d-%H:%M:%S.')+var+'.nc'
    outputfile = outputdir+'ave.'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d.'+var+'.nc'
    print outputfile
    VAR = DataExtractor(themask,inputfile,var).values


    var_b1=np.zeros((jpj,jpi),np.float32)
    var_b2=np.zeros((jpj,jpi),np.float32)

    w_mean=np.zeros((jpj,jpi),np.float32)

    for i in range(jpi):
        for j in range(jpj):
            b1=bottom_1[j,i]
            b2=bottom_2[j,i]
            if water[j,i]:
                var_b1[j,i] = VAR[b1,j,i]
                var_b2[j,i] = VAR[b2,j,i]


    w_mean[water] = (var_b1[water]*e3t_b1[water] + var_b2[water]*e3t_b2[water])/(e3t_b1[water]+e3t_b2[water])

    w_mean[~water] = 1.0e+20

    netcdf4.write_2d_file(w_mean,var,outputfile,themask,fillValue=1e+20,compression=True)

