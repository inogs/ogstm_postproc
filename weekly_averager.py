from commons.Timelist import TimeList
from commons.mask import Mask
from commons.time_averagers import TimeAverager3D, TimeAverager2D
import netCDF4 as NC
from commons import netcdf4

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1

VARLIST=['Ac','CaCO3flux_dic','B1c','N5s','R2c','ppn','O2o','pCO2','pH','DIC','CaCO3flux_alk']
INPUTDIR="/pico/scratch/userexternal/lfeudale/validation/V2C/ANALYSIS/AGGREGATE/"

INPUTDIR="/marconi_scratch/userexternal/gbolzon0/TRANSITION_24/CFR/EAS2/AVE_FREQ_1/"
VARLIST=['P_l']
OUTPUTDIR="/marconi_scratch/userexternal/gbolzon0/TRANSITION_24/CFR/EAS2/AVE_FREQ_2/"

TheMask=Mask('/marconi_scratch/userexternal/gbolzon0/TRANSITION_24/wrkdir/MODEL/meshmask.nc')

TL=TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar="N3n")



#VARLIST=['pH','pCO2']





MONTHLY_REQS = TL.getWeeklyList(5)


for req in MONTHLY_REQS[rank::nranks]:
    indexes,weights=TL.select(req)
    for var in VARLIST:
        if var=='pH': 
            inputvar='PH'
        else:
            inputvar=var
        outfile = OUTPUTDIR + "ave." + req.string + "-12:00:00." + var + ".nc"
        print outfile
        filelist=[]
        for k in indexes:
            t = TL.Timelist[k]
            filename = INPUTDIR + "ave." + t.strftime("%Y%m%d-%H:%M:%S") + "." + inputvar + ".nc"
            filelist.append(filename)
        M3d = TimeAverager3D(filelist, weights, inputvar, TheMask)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask)

