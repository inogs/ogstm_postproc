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
from datetime import datetime

inputdir   = addsep(args.inputdir)
outputdir   = addsep(args.outputdir)
mask   = args.mask
starttime = args.starttime
endtime = args.endtime
var = args.variable

#starttime='2014'
#endtime='2015'
#inputdir='/gpfs/scratch/userexternal/gcoidess/TEST_VINKO_output/'
#var='N1p'

inputdir_bottom=inputdir+'bottom/'
inputdir_top=inputdir+'top/'
#outputdir='/gpfs/scratch/userexternal/gcoidess/TEST_VINKO_output/'
outputdir_bottom = outputdir + 'bottom/'
outputdir_top    = outputdir + 'top/'
#themask = Mask('/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc')
themask = Mask(mask)
jpk, jpj, jpi = themask.shape

TI=TimeInterval(starttime,endtime,'%Y')

TL=TimeList.fromfilenames(TI, inputdir_bottom,"ave*nc",filtervar="N1p")

nFrames=TL.nTimes

matrix_bottom=np.zeros((nFrames,jpj,jpi),np.float32)
matrix_median=np.zeros((jpj,jpi),np.float32)

for iFrame,time in enumerate(TL.Timelist):
    
    inputfile=inputdir_bottom+'ave.'+time.strftime('%Y%m%d-')+ '12:00:00.'+'bottom2d.'+var+'.nc'
    matrix_bottom[iFrame,:,:] = netcdf4.readfile(inputfile, var)
        
matrix_median=np.median(matrix_bottom,axis=0)  #primo indice

outputfile_bottom=outputdir_bottom+'ave.'+'bottom2d_median.'+var+'.nc'       
netcdf4.write_2d_file(matrix_median,var,outputfile_bottom,themask,fillValue=1e+20,compression=True)
print 'median done'

matrix_top=np.zeros((nFrames,jpj,jpi),np.float32)
matrix_top=np.zeros((jpj,jpi),np.float32)

for iFrame,time in enumerate(TL.Timelist):
    
    inputfile=inputdir_top+'ave.'+time.strftime('%Y%m%d-')+ '12:00:00.'+'top2d.'+var+'.nc'
    matrix_bottom[iFrame,:,:] = netcdf4.readfile(inputfile, var)
        
matrix_median=np.median(matrix_top,axis=0)  #primo indice
        
outputfile_top=outputdir_top+'ave.'+'top2d_median.'+var+'.nc'       
netcdf4.write_2d_file(matrix_median,var,outputfile_top,themask,fillValue=1e+20,compression=True)
print 'median done'













