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

    return parser.parse_args()


args = argument()

import numpy as np
from commons.mask import Mask
from commons import netcdf4
from commons.dataextractor import DataExtractor
from commons.Timelist import TimeList,TimeInterval
from commons.utils import addsep
from layer_integral.mapbuilder import MapBuilder
from commons.layer import Layer

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

layer = Layer(0,200)

IngvMask= Mask(maskfile_ingv)
themask = Mask(mask_f)

bottom_indexes_ingv=IngvMask.bathymetry_in_cells()

bottom_1_ingv = bottom_indexes_ingv - 1
bottom_2_ingv = bottom_indexes_ingv - 2

JPK, JPJ, JPI = IngvMask.shape
jpk, jpj, jpi = themask.shape

e3t_b1_ingv=np.zeros((JPJ,JPI),np.float32)
e3t_b2_ingv=np.zeros((JPJ,JPI),np.float32)
water_ingv = IngvMask.mask[0,:,:]
water = themask.mask[0,:,:]
for I in range(JPI):
    for J in range(JPJ):
        B1=bottom_1_ingv[J,I]
        B2=bottom_2_ingv[J,I]
        if water_ingv[J,I]:
            e3t_b1_ingv[J,I] = IngvMask.e3t[B1,J,I]
            e3t_b2_ingv[J,I] = IngvMask.e3t[B2,J,I]

TI=TimeInterval(starttime,endtime,'%Y')
TL=TimeList.fromfilenames(TI, inputdir, '*.nc', filtervar='U',prefix='U')

for time in TL.Timelist[rank::nranks]:
    
    inputfile_U = inputdir+'U'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
    inputfile_T = inputdir+'T'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
    inputfile_V = inputdir+'V'+ time.strftime('%Y%m%d-%H:%M:%S')+'.nc'
    
    outputdir_bottom = outputdir + 'bottom/'
    outputdir_top    = outputdir + 'top/'
    
    outputfile_T_bottom  = outputdir_bottom+ 'T'  + time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    outputfile_S_bottom  = outputdir_bottom+ 'S'  + time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    outputfile_UV_bottom = outputdir_bottom+ 'UV' + time.strftime('%Y%m%d-%H:%M:%S.')+'bottom2d'+'.nc'
    
    outputfile_T_top = outputdir_top  +'T' + time.strftime('%Y%m%d-%H:%M:%S.')+'top2d'+'.nc'
    outputfile_S_top = outputdir_top  +'S' + time.strftime('%Y%m%d-%H:%M:%S.')+'top2d'+'.nc'
    outputfile_UV_top = outputdir_top +'UV'+ time.strftime('%Y%m%d-%H:%M:%S.')+'top2d'+'.nc'
    
    print outputfile_T_bottom
    
    DE_U = DataExtractor(IngvMask,inputfile_U,'vozocrtx')
    DE_T = DataExtractor(IngvMask,inputfile_T,'votemper')
    DE_V = DataExtractor(IngvMask,inputfile_V,'vomecrty')
    DE_S = DataExtractor(IngvMask,inputfile_T,'vosaline')
    
    VAR_U = DE_U.values
    VAR_T = DE_T.values
    VAR_V = DE_V.values
    VAR_S = DE_S.values

    VAR_UV = np.sqrt(VAR_U**2 + VAR_V**2)
    
    DE_UV=DataExtractor(IngvMask,rawdata=VAR_UV)

    Map2d_T = MapBuilder.get_layer_average(DE_T, layer)
    Map2d_S = MapBuilder.get_layer_average(DE_S, layer)
    Map2d_UV = MapBuilder.get_layer_average(DE_UV, layer)

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
    T_mean =  T_mean[:,JPI-jpi:]
    S_mean =  S_mean[:,JPI-jpi:]
    
    Map2d_T  =  Map2d_T[:,JPI-jpi:]
    Map2d_S  =  Map2d_S[:,JPI-jpi:]
    Map2d_UV =  Map2d_UV[:,JPI-jpi:]
    
    UV_mean[~water] = 1.0e+20
    T_mean[~water]  = 1.0e+20
    S_mean[~water]  = 1.0e+20
    
    Map2d_T[~water]  = 1.0e+20
    Map2d_S[~water]  = 1.0e+20
    Map2d_UV[~water] = 1.0e+20

    netcdf4.write_2d_file(UV_mean,'UV',outputfile_UV_bottom,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(T_mean,'T',outputfile_T_bottom,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(S_mean,'S',outputfile_S_bottom,themask,fillValue=1e+20,compression=True)
    
    netcdf4.write_2d_file(Map2d_UV,'UV',outputfile_UV_top,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(Map2d_T,'T',outputfile_T_top,themask,fillValue=1e+20,compression=True)
    netcdf4.write_2d_file(Map2d_S,'S',outputfile_S_top,themask,fillValue=1e+20,compression=True)
    
    
    
    
