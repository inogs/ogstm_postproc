import netCDF4
from bitsea.commons.mask import Mask
import numpy as np
maskfile="/gpfs/work/IscrC_REBIOMED/NRT_EAS6/PREPROC/MASK/ogstm/meshmask.nc"
M=Mask(maskfile)


e3t=M.e3t
e3t[~M.mask]=1.e+20

jpk, jpj, jpi=M.shape
cut = 80 #1/24
ncOUT=netCDF4.Dataset("MED_MFC_006_014_coordinates.nc","w")

ncOUT.createDimension('longitude',jpi-cut);
ncOUT.createDimension('latitude',jpj);
ncOUT.createDimension('depth',jpk);

ncvar=ncOUT.createVariable("longitude",'f', ("longitude",))
setattr(ncvar,"step","0.041666666666666664")
setattr(ncvar, "units", "degrees_east")
setattr(ncvar, "standard_name","longitude")
setattr(ncvar, "axis","X")
ncvar[:] = M.xlevels[0,cut:]

ncvar=ncOUT.createVariable("latitude",'f', ("latitude",))
setattr(ncvar,"step","0.041666666666666664")
setattr(ncvar, "units", "degrees_north")
setattr(ncvar, "standard_name","latitude")
setattr(ncvar, "axis","Y")
ncvar[:] = M.ylevels[:,0]

ncvar=ncOUT.createVariable("depth",'f', ("depth",))
setattr(ncvar, "units", "m")
setattr(ncvar, "positive", "down")
setattr(ncvar, "standard_name","depth")
setattr(ncvar, "axis","Z")
ncvar[:] = M.zlevels

ncvar=ncOUT.createVariable("e1t",'f', ("latitude","longitude"),zlib=True,fill_value=1.e+20)
setattr(ncvar,"units","m")
setattr(ncvar, "long_name","Cell dimension along X axis")
ncvar[:]=M.e1t[:,cut:]

ncvar=ncOUT.createVariable("e2t",'f', ("latitude","longitude"),zlib=True,fill_value=1.e+20)
setattr(ncvar,"units","m")
setattr(ncvar, "long_name","Cell dimension along Y axis")
ncvar[:]=M.e2t[:,cut:]

ncvar=ncOUT.createVariable("e3t",'f', ("depth", "latitude","longitude"),zlib=True,fill_value=1.e+20)
setattr(ncvar,"units","m")
setattr(ncvar, "long_name","Cell dimension along Z axis")
setattr(ncvar, "standard_name","cell_thickness")
ncvar[:]=e3t[:,:, cut:]

setattr(ncOUT,'Conventions'  ,'CF-1.0' )
ncOUT.close()





ncOUT=netCDF4.Dataset("MED_MFC_006_014_mask_bathy.nc","w")

ncOUT.createDimension('longitude',jpi-cut)
ncOUT.createDimension('latitude',jpj)
ncOUT.createDimension('depth',jpk)

ncvar=ncOUT.createVariable("longitude",'f', ("longitude",))
setattr(ncvar,"step","0.041666666666666664")
setattr(ncvar, "units", "degrees_east")
setattr(ncvar, "standard_name","longitude")
setattr(ncvar, "axis","X")
ncvar[:] = M.xlevels[0,cut:]

ncvar=ncOUT.createVariable("latitude",'f', ("latitude",))
setattr(ncvar,"step","0.041666666666666664")
setattr(ncvar, "units", "degrees_north")
setattr(ncvar, "standard_name","latitude")
setattr(ncvar, "axis","Y")
ncvar[:] = M.ylevels[:,0]

ncvar=ncOUT.createVariable("depth",'f', ("depth",))
setattr(ncvar, "units", "m")
setattr(ncvar, "positive", "down")
setattr(ncvar, "standard_name","depth")
setattr(ncvar, "axis","Z")
ncvar[:] = M.zlevels

ncvar=ncOUT.createVariable("mask",'b', ("depth", "latitude","longitude"), zlib=True)
setattr(ncvar, "long_name","Land-sea mask : 1 = sea ; 0 = land")
setattr(ncvar, "standard_name","sea_binary_mask")
setattr(ncvar, "units","1")
ncvar[:]=M.mask[:,:,cut:]

cells_bathy = M.bathymetry_in_cells()
Bathy = M.bathymetry()

CB=cells_bathy.astype(np.float32)
CB[CB==0] = 1.e+20
            
ncvar=ncOUT.createVariable("deptho",'f', ("latitude","longitude"),zlib=True, fill_value=1.0e+20)
setattr(ncvar,"units","m")
setattr(ncvar, "long_name","Bathymetry")
setattr(ncvar, "standard_name","sea_floor_depth_below_geoid")
ncvar[:]=Bathy[:,cut:]

ncvar=ncOUT.createVariable("deptho_lev",'f', ("latitude","longitude"),zlib=True, fill_value=1.0e+20)
setattr(ncvar,"units","1")
setattr(ncvar, "long_name","Bathymetry")
setattr(ncvar, "long_name"    ,"Model level number at sea floor")
setattr(ncvar, "standard_name","model_level_number_at_sea_floor")

ncvar[:]=CB[:,cut:]

setattr(ncOUT,'Conventions'  ,'CF-1.0' )
ncOUT.close()
