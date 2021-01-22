import numpy as np
from commons.mask import Mask
from commons import netcdf4
from commons.dataextractor import DataExtractor


filename = '/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/AVE_FREQ_2/ave.20191226-12:00:00.N1p.nc'

themask = Mask('/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc')

VAR = DataExtractor(themask,filename,'N1p').values

bottom_indexes = themask.bathymetry_in_cells()

bottom_1 = bottom_indexes - 1
bottom_2 = bottom_indexes - 2

ii1 = bottom_1 < 0
ii2 = bottom_2 < 0

bottom_1[ii1] = 0
bottom_2[ii2] = 0

#for i in themask.shape[2]:
#	for j in themask.shape[1]:

jpk, jpj, jpi = themask.shape

e3t_b1=np.zeros((jpj,jpi),np.float32)
e3t_b2=np.zeros((jpj,jpi),np.float32)

var_b1=np.zeros((jpj,jpi),np.float32)
var_b2=np.zeros((jpj,jpi),np.float32)

w_mean=np.zeros((jpj,jpi),np.float32)

for j in range(jpj):
        for i in range(jpi):
		b1=bottom_1[j,i]
		b2=bottom_2[j,i]
		if not ii1[j,i]:
			e3t_b1[j,i] = themask.e3t[b1,j,i]
		if not ii2[j,i]:
			e3t_b2[j,i] = themask.e3t[b2,j,i]		


for j in range(jpj):
        for i in range(jpi):
                b1=bottom_1[j,i]
		b2=bottom_2[j,i]
		if not ii1[j,i]:
                        var_b1[j,i] = VAR[b1,j,i]
                if not ii2[j,i]:
                        var_b2[j,i] = VAR[b2,j,i]
                

w_mean[ii1] = (var_b1[ii1]*e3t_b1[ii1] + var_b2[ii1]*e3t_b2[ii1])/(e3t_b1[ii1]+e3t_b2[ii1])

	
