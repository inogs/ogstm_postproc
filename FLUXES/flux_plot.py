import flux_reader
import pickle
import numpy as np
import glob
import pylab as pl
from commons.Timelist import TimeList

flux_dt =np.dtype([('adv-u',np.float),('adv-v',np.float),('adv-w',np.float),('sed-w',np.float),\
                   ('hdf-x',np.float),('hdf-y',np.float),('zdf-z',np.float)])

Matrices_file="/gpfs/work/OGS18_PRACE_P_0/OPEN_BOUNDARY/preproc_Fluxes/FLUXES/Matrices.pkl"
fid = open(Matrices_file,'rb'); Matrices = pickle.load(fid); fid.close()

INPUTDIR  ="/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_02/wrkdir/MODEL/FLUXES"
TL = TimeList.fromfilenames(None, INPUTDIR, "flux*.nc", prefix="flux.")

flux = flux_reader.read_flux_timeseries(TL.filelist,"N3n",Matrices,flux_dt)
iDard=7

M = flux[iDard]['adv-u'][:14,:,0]

fig,ax=pl.subplots()
im=ax.imshow(M,cmap=pl.get_cmap('bwr',64))
im.set_clim(-10000,10000)
ax.set_ylabel("depth index")
ax.set_xlabel("j index")
fig.colorbar(im)
fig.show()
fig.savefig('Flux_map_N3n.png')

balance=flux_reader.flux_two_timeseries(flux[iDard]['adv-u']  + flux[iDard]['hdf-x'])
Hov = flux_reader.flux_hovmoeller(flux[iDard]['adv-u'])#  + flux[iDard]['hdf-x'])

fig,ax=pl.subplots()
ax.plot(balance[:,0],'r',label='lower exiting ')
ax.plot(balance[:,1],'b',label='upper entering')
ax.plot(balance.sum(axis=1), 'g', label='Net')
ax.grid()
ax.legend()
ax.set_xlabel("month")
ax.set_ylabel("mmol/s")
ax.set_title("Nitrate flux")
fig.show()
fig.savefig("Nitrate_monthly_flux_dardanelles.png")

import matplotlib.dates as mdates
from commons.mask import Mask
from datetime import datetime
TheMask=Mask("/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_02/wrkdir/MODEL/meshmask.nc",loadtmask=False)
L=TL.Timelist
L.append(datetime(2018,1,15))
fig,ax=pl.subplots()

xs,ys = np.meshgrid(mdates.date2num(L), TheMask.zlevels[:14])
M=np.zeros((14,13), np.float32)
M[:,:12]=Hov[:14,:]
#M = Hov[:14,:]

M[0,0]=10000
M[0,11]=10000
M[M==0]=np.nan
quadmesh = ax.pcolormesh(xs, ys, np.ma.masked_invalid(M),shading='flat',vmin=-20000,vmax=20000, cmap=pl.get_cmap('bwr',64))
#quadmesh=ax.imshow(Hov[:14,:], extent=[xs.min(), xs.max(), ys.min(), ys.max()], cmap=pl.get_cmap('bwr',64))
ax.set_xticks(xs[0,:-1])
ax.set_xlim(xs.min(), xs.max()+50)
fig.colorbar(quadmesh)
ax.xaxis_date()
ax.invert_yaxis()
#x.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
fig.show()

#im.set_clim(-20000,20000)
ax.set_ylabel("depth index")
#ax.set_xlabel("j index")



