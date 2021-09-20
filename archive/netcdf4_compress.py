import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates netCDF4 compressed files

    Parallel executable, can be called by mpirun.
   ''',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help ='The directory wrkdir/MODEL/AVE_FREQ_1/ where chain has run.'
                                )
    parser.add_argument(   '--outputdir',"-o",
                                type = str,
                                required = True,
                                help = 'Path of existing dir')
    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "*.nc",
                                help = 'ave*.N1p.nc')
    parser.add_argument(   '--cutlevel',"-c",
                                required= False, 
                                type = int,
                                default = None,
                                help = 'depth levels on output files')  
 
    return parser.parse_args()


args = argument()

import netCDF4
import numpy as np
import os
from commons.utils import addsep
import glob
from commons.netcdf4 import lon_dimension_name, lat_dimension_name, depth_dimension_name

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1

INPUTDIR  = addsep(args.inputdir)
OUTPUTDIR = addsep(args.outputdir)
PATH_NAME = args.filelist
os.chdir(INPUTDIR)
FILELIST=glob.glob(PATH_NAME)
FILELIST.sort()


def WRITE_AVE(inputfile, outfile,var):
    
    #De=DataExtractor(TheMask,filename,var)
    
    ncIN = netCDF4.Dataset(inputfile,"r")    
    ncOUT = netCDF4.Dataset(outfile,"w",format="NETCDF4")
    
    setattr(ncOUT,"Convenctions","COARDS")
    if "DateStart" in ncIN.ncattrs():
        setattr(ncOUT,"DateStart",ncIN.DateStart)
        setattr(ncOUT,"Date__End",ncIN.Date__End)
    
    DIMS=ncIN.dimensions
    for dimName,dimObj in DIMS.items():
        ncOUT.createDimension(dimName,dimObj.size)
    lon_orig_name=lon_dimension_name(ncIN)
    lat_orig_name=lat_dimension_name(ncIN)
    depth_orig_name=depth_dimension_name(ncIN)


    if 'depth' in ncIN.variables:
        ncvar = ncOUT.createVariable('depth'   ,'f', ('depth',))
        setattr(ncvar,'units','meter')
        setattr(ncvar,'positive','down')
        ncvar[:]=np.array(ncIN[depth_orig_name])
    
    ncvar = ncOUT.createVariable(lon_orig_name   ,'f',   (lon_orig_name,))
    setattr(ncvar,'units','degrees_east')
    setattr(ncvar,'long_name','Longitude')
    ncvar[:]=np.array(ncIN[lon_orig_name])

    ncvar = ncOUT.createVariable(lat_orig_name   ,'f',   (lat_orig_name,))
    setattr(ncvar,'units','degrees_north')
    setattr(ncvar,'long_name','Latitude')
    ncvar[:]=np.array(ncIN[lat_orig_name])


    OUT = np.array(ncIN[var])
    if 'time' in ncIN.dimensions:
        if len(OUT.shape)==4:
            ncvar = ncOUT.createVariable(var, 'f', ('time','depth',lat_orig_name,lon_orig_name),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'long_name',var)
            ncvar[:] = OUT
        if len(OUT.shape)==3:
            ncvar = ncOUT.createVariable(var, 'f', ('time',lat_orig_name,lon_orig_name),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'long_name',var)
            ncvar[:] =  OUT
    else:
        ncOUT.createDimension('time',0)
        if len(OUT.shape)==3:
            ncvar = ncOUT.createVariable(var, 'f', ('time','depth',lat_orig_name,lon_orig_name),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'long_name',var)
            ncvar[0,:] = OUT
        if len(OUT.shape)==2:
            ncvar = ncOUT.createVariable(var, 'f', ('time',lat_orig_name,lon_orig_name),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'long_name',var)
            ncvar[0,:] =  OUT
    ncIN.close()
    ncOUT.close()

def WRITE_RST_DA(inputfile, outfile,var,jkcut=None):
    
    ncIN = netCDF4.Dataset(inputfile,"r")    
    ncOUT = netCDF4.Dataset(outfile,"w",format="NETCDF4")

    DIMS=ncIN.dimensions
    for dimName,dimObj in DIMS.items():
        if ((jkcut is not None ) & (dimName in ["z","depth"])) :
            ncOUT.createDimension(dimName,jkcut)
        else:
            ncOUT.createDimension(dimName,dimObj.size)

    if not DIMS.has_key('time'):
        ncOUT.createDimension('time',1)
    dims=('time',depth_dimension_name(ncIN),lat_dimension_name(ncIN) ,lon_dimension_name(ncIN))
    ncvar = ncOUT.createVariable("TRN" + var, 'f', dims ,zlib=True, fill_value=1.0e+20)
    setattr(ncvar,'missing_value',ncvar._FillValue)
    if var in ncIN.variables:
        x=np.array(ncIN[var])
    else:
        x=np.array(ncIN["TRN" + var])

    if (len(x.shape)==4):
        ncvar[:] = x[:,:jkcut,:,:]
    else:
        ncvar[0,:] = x[:jkcut,:,:]
    ncIN.close()
    ncOUT.close()

def WRITE_RST(inputfile, outfile,var):
    '''
    Valid for true restarts (51 variables, double)
    '''
    
    ncIN = netCDF4.Dataset(inputfile,"r")    
    ncOUT = netCDF4.Dataset(outfile,"w",format="NETCDF4")
        
    DIMS=ncIN.dimensions
    for dimName,dimObj in DIMS.items():
        ncOUT.createDimension(dimName,dimObj.size)

    ncvar = ncOUT.createVariable("TRN" + var, 'd', ('time','z','y','x'),zlib=True, fill_value=1.0e+20)            
    setattr(ncvar,'missing_value',ncvar._FillValue)
    ncvar[:] = np.array(ncIN["TRN" + var])
    ncIN.close()
    ncOUT.close()
    

for filename in FILELIST[rank::nranks]:
    basename=os.path.basename(filename)
    outfile=OUTPUTDIR + basename
    print(outfile)
    prefix, datestr, var, _ = basename.rsplit(".")
    if prefix == 'ave':
        WRITE_AVE(filename, outfile, var)
    if prefix == "RST":
        if datestr.count("0000"):
            WRITE_RST_DA(filename, outfile, var, args.cutlevel)
        else:
            WRITE_RST(filename, outfile, var)
    if prefix in ["RST_after", "RSTbefore"]:
        WRITE_RST_DA(filename, outfile, var, args.cutlevel)

