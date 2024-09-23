from bitsea.commons.mask import Mask
from bitsea.commons.submask import SubMask
from bitsea.basins import V2 as OGS
import numpy as np
from bitsea.commons.utils import writetable

maskfile="/g100_work/OGS21_PRACE_P/CLIMA_100/meshmask.nc"

TheMask=Mask(maskfile)

#basins
nSUB = len(OGS.P.basin_list)
jpk,jpj,jpi =TheMask.shape
mask200_2D = TheMask.mask_at_level(200.0)
dtype = [(sub.name, np.bool) for sub in OGS.P]
SUB = np.zeros((jpj,jpi),dtype=dtype)
mask0 = TheMask.cut_at_level(0)

for sub in OGS.Pred:
    SUB[sub.name]  = SubMask(sub,maskobject=mask0).mask[0,:]
    if 'atl' in sub.name: continue
    SUB['med'] = SUB['med'] | SUB[sub.name]

COASTNESS_LIST=['coast','open_sea','everywhere']

dtype = [(coast, np.bool) for coast in COASTNESS_LIST]
COASTNESS = np.ones((jpj,jpi),dtype=dtype)
COASTNESS['coast']     = ~mask200_2D
COASTNESS['open_sea']  =  mask200_2D
nCoast= len(COASTNESS_LIST)

AREA = np.zeros((nSUB,nCoast), np.float32)

for isub, sub in enumerate(OGS.P):
    for icoast, coast in enumerate(COASTNESS_LIST):
        ii=COASTNESS[coast] & SUB[sub.name]
        AREA[isub, icoast] = TheMask.area[ii].sum()


row_names=[sub.name for sub in OGS.P.basin_list]
writetable('aree_mq.txt', AREA, row_names, COASTNESS_LIST, fmt="%20.2f")
        
