import numpy as np
import netCDF4
from bitsea.commons import netcdf4
from datetime import datetime, timedelta
from bitsea.commons.Timelist import TimeList
obs_file="/g100_scratch/userexternal/ateruzzi/EAT_DA/ENS_CHLprof_IC/Obs2016_short_perGP/ToAssimilate/profile_P_Chl.obs"
dtype=[("day","U10"),('hr',"U8"),("z",np.float32),('chl',np.float32),('err',np.float32)]

OBS = np.loadtxt(obs_file, dtype)
obs_days_string, index, inverse_index = np.unique(OBS['day'],  return_index=True, return_inverse=True)
obs_timelist=[datetime.strptime(s, "%Y-%m-%d")  for s in obs_days_string]

INPUTDIR="/g100_scratch/userexternal/ateruzzi/EAT_DA/ENS_CHLprof_IC/Obs2016_short_perGP/"


modelfile=INPUTDIR + "result_0001.nc"

time_seconds = netcdf4.readfile(modelfile, 'time')
model_depth = -netcdf4.readfile(modelfile, 'z')[0,:,0,0]
model_depth = model_depth[-1::-1]


reftime=datetime(2016,1,1,0,0,0)
SHIFT_OBS = 0.494 - 1.0e-5 # to have something meaningful

timelist = [reftime + timedelta(seconds=deltat) for deltat in time_seconds]
TL =TimeList(timelist)
coupled_list = TL.couple_with(obs_timelist)
d, indexes = coupled_list[1]
ii = inverse_index==indexes[0]
chl_obs =  OBS[ii]['chl'][-1::-1] - SHIFT_OBS
z_obs   = -OBS[ii]['z'][-1::-1]

itime=4
model_chl = netcdf4.readfile(modelfile, 'total_chlorophyll_calculator_result')[itime,:,0,0]
model_chl = model_chl[-1::-1]
prior = np.interp(z_obs,model_depth,model_chl)
itime=5
model_chl = netcdf4.readfile(modelfile, 'total_chlorophyll_calculator_result')[itime,:,0,0]
model_chl = model_chl[-1::-1]
posterior = np.interp(z_obs,model_depth,model_chl)

if True:
    import pylab as pl
    fig,ax=pl.subplots()
    
    ax.plot(chl_obs, z_obs,label='obs')
    ax.plot(model_chl, model_depth, label='model')
    ax.plot(posterior, z_obs,'.', label='model interp')
    ax.legend()
    ax.set_ylim([0,300])
    ax.invert_yaxis()
    fig.savefig('pippo.png')

m = 10
nPoints = len(z_obs)
prior_ensemble    =np.zeros((m,nPoints),np.float32)
posterior_ensemble=np.zeros((m,nPoints),np.float32)

for ie in range(m):
    modelfile = "%sresult_%04d.nc" %(INPUTDIR, ie+1)
    itime=4
    model_chl = netcdf4.readfile(modelfile, 'total_chlorophyll_calculator_result')[itime,:,0,0]
    model_chl = model_chl[-1::-1]
    prior_ensemble[ie,:] = np.interp(z_obs,model_depth,model_chl)
    itime=5
    model_chl = netcdf4.readfile(modelfile, 'total_chlorophyll_calculator_result')[itime,:,0,0]
    model_chl = model_chl[-1::-1]
    posterior_ensemble[ie,:] = np.interp(z_obs,model_depth,model_chl)


outfile = "out_fabm.nc"
ncOUT = netCDF4.Dataset(outfile,'w')
ncOUT.createDimension("m",m)
ncOUT.createDimension("n",nPoints)
ncvar = ncOUT.createVariable("prior_ensemble",'f',('m','n'))
ncvar[:] = prior_ensemble
ncvar = ncOUT.createVariable("posterior_ensemble",'f',('m','n'))
ncvar[:] = posterior_ensemble
ncvar = ncOUT.createVariable("observations",'f',('n',))
ncvar[:] = chl_obs

ncOUT.close()

