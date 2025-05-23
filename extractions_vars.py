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
from bitsea.commons.mask import Mask
from bitsea.commons import netcdf4
from bitsea.commons.dataextractor import DataExtractor
from bitsea.commons.Timelist import TimeList,TimeInterval
from bitsea.commons.utils import addsep
from bitsea.layer_integral.mapbuilder import MapBuilder
from bitsea.commons.layer import Layer


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

layer = Layer(0,200)

#themask = Mask.from_file('/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc')
themask= Mask.from_file(mask)
bottom_indexes = themask.bathymetry_in_cells() - 1

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
    outputdir_bottom = outputdir +starttime+'_'+endtime+'/'+'bottom/'
    outputdir_top = outputdir +starttime+'_'+endtime+'/'+'top/'
    outputfile_bottom = outputdir_bottom +'ave.'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d.'+var+'.nc'
    
    print outputfile_bottom
    
    DE = DataExtractor(themask,inputfile,var)
    VAR = DE.values
    
    outputfile_top = outputdir_top +'ave.'+ time.strftime('%Y%m%d-%H:%M:%S.')+'top2d.'+var+'.nc'
    Map2d = MapBuilder.get_layer_average(DE, layer)

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
    Map2d[~water] = 1.0e+20

    netcdf4.write_2d_file(w_mean,var,outputfile_bottom,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(Map2d, var,   outputfile_top,themask,fillValue=1e+20,compression=True)

