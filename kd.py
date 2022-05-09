import numpy as np
from commons.utils import data_for_linear_interp
from datetime import datetime
from commons.mask import Mask
from commons.dataextractor import DataExtractor
from commons import netcdf4

INPUTDIR="/g100_scratch/userexternal/gbolzon0/V9C/2019/TEST_03/wrkdir/MODEL/AVE_FREQ_3/"
OUTDIR ="/g100_scratch/userexternal/gbolzon0/V9C/KD/"
TheMask = Mask('/g100_work/OGS_prod100/OPA/V9C/RUNS_SETUP/PREPROC/MASK/meshmask.nc')
jpk,jpj,jpi = TheMask.shape
mask0 = TheMask.mask_at_level(0)

opt_mask = np.zeros((jpk,jpj,jpi),np.bool)
bottom= TheMask.bathymetry_in_cells()
for ji in range(jpi):
    for jj in range(jpj):
        if mask0[jj,ji]:
            b = bottom[jj,ji]
            opt_mask[:b+1,jj,ji] = True



freq_nanom = [250, 325, 350, 375, 400, 425, 450, 475, 500, 525, 550, 575, 600, 625,
       650, 675, 700, 725, 775, 850, 950, 1050, 1150, 1250, 1350, 1450, 1550, 1650,
       1750, 1900, 2200, 2900, 3700]



def load_data(prefix,index_freq, dateobj):
    var = "%s_%04d" %(prefix, freq_nanom[index_freq])
    filename = "%save.%s.%s.nc" %(INPUTDIR,dateobj.strftime("%Y%m%d-%H:%M:%S"),var)
    print(filename,flush=True)
    return DataExtractor(TheMask,filename, var).values


def get_E(dateobj, interp_data):
    freq_before, freq_after, w = interp_data
    E_before = load_data("Ed", freq_before, dateobj)
    E_after  = load_data("Ed", freq_after , dateobj)
    Ed = E_before*(1-w) + w*E_after
    Ed[~opt_mask] = 1.e+20
    
    E_before = load_data("Es", freq_before, dateobj)
    E_after  = load_data("Es", freq_after , dateobj)
    Es = E_before*(1-w) + w*E_after    
    Es[~opt_mask] = 1.e+20
    return Ed + Es



d = datetime(2019,1,1,12)

for wavelengh in [380, 412, 490]:
    interp_data = data_for_linear_interp(freq_nanom,wavelengh)
    E = get_E(d, interp_data)
    KD = np.ones((jpk,jpj,jpi),np.float32)*1.e-08
    jk_lim = TheMask.getDepthIndex(500.)


    KD[:jk_lim,:,:] = -np.log(E[1:jk_lim+1,:]/E[0:jk_lim,:])/TheMask.e3t[:jk_lim,:]
    KD[~TheMask.mask] = 1.e+20
# check
    for k in range(10):
        junk = KD[k,:,:]
        max_val = junk[TheMask.mask[k,:,:]].max()
        ii = KD[k,:,:] == max_val
        print(k, np.nonzero(ii))


    varname="kd%s" %wavelengh
    outfile ="%save.%s.%s.nc" %(OUTDIR,d.strftime("%Y%m%d-%H:%M:%S"),varname)
    print(outfile)
    netcdf4.write_3d_file(KD, varname, outfile, TheMask, compression=True)




# for ji in range(jpi):
#     for jj in range(jpj):
#         if mask0[jj,ji]:
#             for jk in range(jk_lim):
#                 KD[jk,jj,ji] = -np.log(E[jk+1,jj,ji]/E[jk,jj,ji])/TheMask.e3t[jk,jj,ji]
                
                
    