import numpy as np
from commons.mask import Mask
from commons.dataextractor import DataExtractor
import Sat.SatManager as Satmodule
import netCDF4


maskfile="/g100_work/OGS_prod100/OPA/V9C/RUNS_SETUP/PREPROC/MASK/meshmask.nc"
TheMask=Mask(maskfile)
coastmask = TheMask.mask_at_level(200.0)
jpk,jpj,jpi = TheMask.shape

DIR="/g100_scratch/userexternal/sspada00/GHOSH/20220511.24x116x10h/AVE_FREQ_1/ENSEMBLE/"

satfile="/gss/gss_work/DRES_OGS_BiGe/Observations/TIME_RAW_DATA/ONLINE_V8C/SAT/CHL/MULTISENSOR/1Km/DT/DAILY/CHECKED_24/20190122_d-OC_CNR-L3-CHL-MedOC4AD4_MULTI_1KM-MED-DT-v02.nc"

m = 10
modvarname="P2l"
satvarname="CHL"
timestr="20190122-12:00:00"




for ie in range(1):
    modfile="%save%03d.%s.%s.nc" %(DIR,ie,timestr,modvarname)
    Model = DataExtractor(TheMask,filename=modfile, varname=modvarname).values[0,:]
    
Sat   = Satmodule.readfromfile(satfile,var=satvarname)



cloudsLand = (np.isnan(Sat)) | (Sat > 1.e19) | (Sat<0)
modelLand  = np.isnan(Model) #lands are nan
nodata     = cloudsLand | modelLand
selection = ~nodata & coastmask

nPoints= selection.sum()
prior_ensemble=np.zeros((nPoints,m),np.float32)
for ie in range(m):
    modfile="%save%03d.%s.%s.nc" %(DIR,ie,timestr,modvarname)
    print(modfile)
    Model = DataExtractor(TheMask,filename=modfile, varname=modvarname).values[0,:]
    prior_ensemble[:,ie]=Model[selection]

timestr="20190123-12:00:00"
posterior_ensemble=np.zeros((nPoints,m),np.float32)
for ie in range(m):
    modfile="%save%03d.%s.%s.nc" %(DIR,ie,timestr,modvarname)
    print(modfile)
    Model = DataExtractor(TheMask,filename=modfile, varname=modvarname).values[0,:]
    posterior_ensemble[:,ie]=Model[selection]







ncOUT = netCDF4.Dataset('out.nc','w')
ncOUT.createDimension("m",m)
ncOUT.createDimension("n",nPoints)
ncvar = ncOUT.createVariable("prior_ensemble",'f',('n','m'))
ncvar[:] = prior_ensemble
ncvar = ncOUT.createVariable("posterior_ensemble",'f',('n','m'))
ncvar[:] = posterior_ensemble
ncvar = ncOUT.createVariable("observations",'f',('n',))
ncvar[:] = Sat[selection]

ncOUT.close()



