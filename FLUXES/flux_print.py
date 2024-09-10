import flux_reader
from bitsea.commons.Timelist import TimeList, TimeInterval
import numpy as np
import pickle
from bitsea.commons import season
from bitsea.commons import timerequestors
from bitsea.commons.utils import writetable
iDard=7

flux_dt =np.dtype([('adv-u',np.float),('adv-v',np.float),('adv-w',np.float),('sed-w',np.float),\
                   ('hdf-x',np.float),('hdf-y',np.float),('zdf-z',np.float)])

Matrices_file="/gpfs/work/OGS18_PRACE_P_0/OPEN_BOUNDARY/preproc_Fluxes/FLUXES/Matrices.pkl"
fid = open(Matrices_file,'rb'); Matrices = pickle.load(fid); fid.close()

INPUTDIR  ="/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/MODEL/FLUXES"
TI = TimeInterval("20170101","20180101","%Y%m%d")
TL = TimeList.fromfilenames(TI, INPUTDIR, "flux*.nc", prefix="flux.")

if TL.inputFrequency == 'daily': TimeIntervalLength=86400
if TL.inputFrequency == 'monthly': TimeIntervalLength=86400*31 # can be improved

LUDWIG_INPUT_KTy={"N1p": 0.2, "N3n":13, "N5s":13, "O3c":3363.8, "O3h": 360.25}
LUDWIG_INPUT={}
w= 1.0e+12;
t = 1./(365 * 86400)
n = 1./14
p = 1./31
s = 1./28
cn = w*n
cp = w*p
cs = w*s
ca = w  
cc = w    
LUDWIG_INPUT['N1p'] =LUDWIG_INPUT_KTy["N1p"]*cp # mmol/y
LUDWIG_INPUT['N3n'] =LUDWIG_INPUT_KTy["N3n"]*cn # mmol/y
LUDWIG_INPUT['N5s'] =LUDWIG_INPUT_KTy["N5s"]*cs # mmol/y
LUDWIG_INPUT['O3h'] =LUDWIG_INPUT_KTy["O3h"]*ca #mg/y
LUDWIG_INPUT['O3c'] =LUDWIG_INPUT_KTy["O3c"]*cc #mg/y

var="N1p"
flux = flux_reader.read_flux_timeseries(TL.filelist, var,Matrices,flux_dt)
balance = flux_reader.flux_two_timeseries(flux[iDard]['adv-u'])


print "%s flux/LUDWIG  =%f" %(var, balance.sum()*TimeIntervalLength/LUDWIG_INPUT[var] )
VARLIST=["N1p","N3n","N5s","O3h","O3c"]
nvar= len(VARLIST)
 
for var in VARLIST:
    flux = flux_reader.read_flux_timeseries(TL.filelist, var,Matrices,flux_dt)
    balance = flux_reader.flux_two_timeseries(flux[iDard]['adv-u']+flux[iDard]['hdf-x'])
    mmoly = balance.sum()*TimeIntervalLength
    print "%s flux Gmol/y = %f flux/LUDWIG  = %f" %(var, mmoly*1.e-12, mmoly/LUDWIG_INPUT[var] )


Seas_obj=season.season()
nSeas = Seas_obj.numbers_season

for var in VARLIST:
    TABLE=np.zeros((nSeas,2), np.float32)
    for iSeas in range(nSeas):
        req=timerequestors.Clim_season(iSeas,Seas_obj)
        ii,w = TL.select(req)
        filelist= [ TL.filelist[k] for k in ii ]
        flux = flux_reader.read_flux_timeseries(filelist, var,Matrices,flux_dt)
        #balance = flux_reader.flux_two_timeseries(flux[iDard]['adv-u']+flux[iDard]['hdf-x'])
        HOV = flux_reader.flux_hovmoeller(flux[iDard]['adv-u']+flux[iDard]['hdf-x'])
        TABLE[iSeas,0] = HOV[  :6,:].sum()
        TABLE[iSeas,1] = HOV[6:14,:].sum()
    TABLE_Gmoly = TABLE*TimeIntervalLength/1.e+12
    rows_names_list = Seas_obj.SEASON_LIST_NAME
    column_names_list=["Upper","Lower"]
    writetable(var + ".txt", TABLE_Gmoly, rows_names_list, column_names_list)

    


