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

    return parser.parse_args()


args = argument()

import numpy as np
from bitsea.commons.mask import Mask
from bitsea.commons import netcdf4
from bitsea.commons.dataextractor import DataExtractor
from bitsea.commons.Timelist import TimeList,TimeInterval
from bitsea.commons.utils import addsep
from datetime import datetime

inputdir   = addsep(args.inputdir)
outputdir   = addsep(args.outputdir)
mask   = args.mask
starttime = args.starttime
endtime = args.endtime

inputdir_bottom=inputdir+starttime+'_'+endtime+'/'+'bottom/'
inputdir_top=inputdir+starttime+'_'+endtime+'/'+'top/'

outputdir_bottom = outputdir +starttime+'_'+endtime+'/'+ 'bottom/'
outputdir_top    = outputdir +starttime+'_'+endtime+'/'+ 'top/'

themask = Mask(mask)
jpk, jpj, jpi = themask.shape

TI=TimeInterval(starttime,endtime,'%Y')
TL=TimeList.fromfilenames(TI, inputdir_bottom,"*nc",prefix='T',filtervar="T")

nFrames=TL.nTimes

matrix_bottom=np.zeros((nFrames,jpj,jpi),np.float32)
matrix_top=np.zeros((nFrames,jpj,jpi),np.float32)

print 'charge done'

for var in 'T', 'S', 'UV':
    
    outputfile_bottom_P05=outputdir_bottom+'P05_b.'+var+'.nc'
    outputfile_bottom_P50=outputdir_bottom+'P50_b.'+var+'.nc'
    outputfile_bottom_P95=outputdir_bottom+'P95_b.'+var+'.nc'

    outputfile_top_P05=outputdir_top+'P05_t.'+var+'.nc'
    outputfile_top_P50=outputdir_top+'P50_t.'+var+'.nc'
    outputfile_top_P95=outputdir_top+'P95_t.'+var+'.nc'
    
    for iFrame,time in enumerate(TL.Timelist):
        
        inputfile_bottom=inputdir_bottom+var+time.strftime('%Y%m%d-')+ '12:00:00.'+'bottom2d.nc'
        inputfile_top=   inputdir_top   +var+time.strftime('%Y%m%d-')+ '12:00:00.'+'top2d.nc'
        matrix_bottom[iFrame,:,:] = netcdf4.readfile(inputfile_bottom, var)
        matrix_top[iFrame,:,:]    = netcdf4.readfile(inputfile_top,    var)
    
    print 'forloop done'
    
    P5_b,P50_b,P95_b=np.percentile(matrix_bottom,[5,50,95],axis=0)  
    P5_t,P50_t,P95_t=np.percentile(matrix_top,   [5,50,95],axis=0)
    
    netcdf4.write_2d_file( P5_b,var,outputfile_bottom_P05,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(P50_b,var,outputfile_bottom_P50,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(P95_b,var,outputfile_bottom_P95,themask,fillValue=1e+20,compression=True)
    
    netcdf4.write_2d_file( P5_t,var,outputfile_top_P05,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(P50_t,var,outputfile_top_P50,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(P95_t,var,outputfile_top_P95,themask,fillValue=1e+20,compression=True)


print 'median done'








