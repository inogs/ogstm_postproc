import numpy as np
from commons.mask import Mask
from commons import netcdf4

VAR = netcdf4.readfile('/gpfs/scratch/userexternal/gbolzon0/REA_24/TEST_22/wrkdir/MODEL/AVE_FREQ_2/ave.20191226-12:00:00.N1p.nc', 'N1p')

themask = Mask('/gpfs/work/IscrC_REBIOMED/REANALISI_24/PREPROC/MASK/gdept_3d/ogstm/meshmask.nc')

bottom_indexes = themask.bathymetry_in_cells()

bottom_1 = bottom_indexes - 1
bottom_2 = bottom_indexes - 2

bottom_1_sos = np.where(bottom_1 < 0, 0, bottom_1)
bottom_2_sos = np.where(bottom_1 < 0, 0, bottom_2)


