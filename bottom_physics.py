import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Create 2d files of bottom (n-1 and n-2) variables (UV=sqrt(U^2+V^2),Temperature and salinity) in a timelist 
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
    parser.add_argument(   '--Mask', '-M',
                                type = str,
                                required = True,
                                help = ''' Name of the forcings mesh of the meshmask used to generate Forcings'''
                                )
    
    parser.add_argument(   '--mask', '-m',
                                type = str,
                                required = True,
                                help = ''' Name of the final mesh of the meshmask to generate files'''
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
    
    #parser.add_argument(   '--variable', '-v',
    #                            type = str,
    #                            required = True,
    #                            help = ''' Variable to extract in the input file'''

    #                            )

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

inputdir        = addsep(args.inputdir)
outputdir       = addsep(args.outputdir)
maskfile_ingv   = args.Mask
mask_f          = args.mask
starttime       = args.starttime
endtime         = args.endtime

#maskfile_ingv='/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/ogstm/meshmask_INGVfor_ogstm.nc'
IngvMask= Mask(maskfile_ingv)

themask = Mask(mask_f)
#bottom_indexes = themask.bathymetry_in_cells()
bottom_indexes_ingv=IngvMask.bathymetry_in_cells()


bottom_1_ingv = bottom_indexes_ingv - 1
bottom_2_ingv = bottom_indexes_ingv - 2

JPK, JPJ, JPI = IngvMask.shape
jpk, jpj, jpi = themask.shape

e3t_b1_ingv=np.zeros((JPJ,JPI),np.float32)
e3t_b2_ingv=np.zeros((JPJ,JPI),np.float32)
water_ingv = IngvMask.mask[0,:,:]
water = themask[0,:,:]
for I in range(JPI):
    for J in range(JPJ):
        B1=bottom_1_ingv[J,I]
        B2=bottom_2_ingv[J,I]
        if water_ingv[J,I]:
            e3t_b1_ingv[J,I] = IngvMask.e3t[B1,J,I]
            e3t_b2_ingv[J,I] = IngvMask.e3t[B2,J,I]
            
            
#var='N1p'
#inputdir='/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/FORCINGS/'
#outputdir='/gpfs/scratch/userexternal/gcoidess/TEST_VINKO_output_phys/'
#starttime='2014'
#endtime='2015'

TI=TimeInterval(starttime,endtime,'%Y')
TL=TimeList.fromfilenames(TI, inputdir, '*.nc', filtervar='U',prefix='U')

for time in TL.Timelist[rank::nranks]:
    #U20190623-12:00:00.nc
    
    inputfile_U = inputdir+'U'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
    inputfile_T = inputdir+'T'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
    inputfile_V = inputdir+'V'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
     
    #outputfile_U = outputdir+'U'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    outputfile_T = outputdir+'T'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    #outputfile_V = outputdir+''+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    outputfile_S = outputdir+'S'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    outputfile_UV = outputdir+'UV'+ time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    
    print outputfile_T
    
    VAR_U = DataExtractor(IngvMask,inputfile_U,'vozocrtx').values
    VAR_T = DataExtractor(IngvMask,inputfile_T,'votemper').values
    VAR_V = DataExtractor(IngvMask,inputfile_V,'vomecrty').values
    VAR_S = DataExtractor(IngvMask,inputfile_T,'vosaline').values

    VAR_UV = np.sqrt(VAR_U**2 + VAR_V**2)

    var_b1_T=np.zeros((JPJ,JPI),np.float32)
    var_b2_T=np.zeros((JPJ,JPI),np.float32)
    var_b1_S=np.zeros((JPJ,JPI),np.float32)
    var_b2_S=np.zeros((JPJ,JPI),np.float32)
    var_b1_UV=np.zeros((JPJ,JPI),np.float32)
    var_b2_UV=np.zeros((JPJ,JPI),np.float32)

    UV_mean=np.zeros((JPJ,JPI),np.float32) #module
    T_mean=np.zeros((JPJ,JPI),np.float32)  #Temperature 
    S_mean=np.zeros((JPJ,JPI),np.float32)  #SALINIY
    
    for I in range(JPI):
        for J in range(JPJ):
            B1=bottom_1_ingv[J,I]
            B2=bottom_2_ingv[J,I]
            if water_ingv[J,I]:
                var_b1_T[J,I] = VAR_T[B1,J,I]
                var_b2_T[J,I] = VAR_T[B2,J,I]
                var_b1_S[J,I] = VAR_S[B1,J,I]
                var_b2_S[J,I] = VAR_S[B2,J,I]
                var_b1_UV[J,I] = VAR_UV[B1,J,I]
                var_b2_UV[J,I] = VAR_UV[B2,J,I]
    
    UV_mean[water_ingv] = (var_b1_UV[water_ingv]*e3t_b1_ingv[water_ingv] + var_b2_UV[water_ingv]*e3t_b2_ingv[water_ingv])/(e3t_b1_ingv[water_ingv]+e3t_b2_ingv[water_ingv])
    T_mean[water_ingv]  = (var_b1_T[water_ingv]*e3t_b1_ingv[water_ingv]  + var_b2_T[water_ingv]*e3t_b2_ingv[water_ingv]) /(e3t_b1_ingv[water_ingv]+e3t_b2_ingv[water_ingv])
    S_mean[water_ingv]  = (var_b1_S[water_ingv]*e3t_b1_ingv[water_ingv]  + var_b2_S[water_ingv]*e3t_b2_ingv[water_ingv]) /(e3t_b1_ingv[water_ingv]+e3t_b2_ingv[water_ingv])
    
    
    UV_mean = UV_mean[:,JPI-jpi:]
    T_mean = T_mean[:,JPI-jpi:]
    S_mean = S_mean[:,JPI-jpi:]
    
    UV_mean[~water] = 1.0e+20
    T_mean[~water]  = 1.0e+20
    S_mean[~water]  = 1.0e+20
        
    #rho = rho[:jpk,:,JPI-jpi:]
    netcdf4.write_2d_file(UV_mean,'UV',outputfile_UV,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(T_mean,'T',outputfile_T,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(S_mean,'S',outputfile_S,themask,fillValue=1e+20,compression=True)

