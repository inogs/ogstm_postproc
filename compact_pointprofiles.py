import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates a single pkl file, containing the overall time series, 
    for every variable in PROFILES.
    Then, in OUTDIR/txt/ it saves Hovmoeller matrices in txt files,
    for every station in pointlist file.
    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = '/some/path/with/STAT_PROFILES')

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = 'Output directory'
                                )
    parser.add_argument(   '--pointlist',"-p",
                                type = str,
                                required = True,
                                help = '''Path of the text file listing the the points where extract point profiles''')

    return parser.parse_args()

args = argument()


from commons.Timelist import TimeInterval,TimeList
import netCDF4
import numpy as np
from commons import netcdf4
from maskload import *
import pickle,os
from commons.utils import addsep
try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1




INPUTDIR=addsep(args.inputdir)
OUTDIR=addsep(args.outdir)

os.system("mkdir -p " + OUTDIR)
os.system("mkdir -p " + OUTDIR + "txt/")

TI = TimeInterval("1900","2150","%Y")
TL=TimeList.fromfilenames(TI,INPUTDIR, "ave*nc")

nFrames = TL.nTimes

def get_info(filename):
    D = netCDF4.Dataset(filename)
    Ordered_DICT=D.variables
    VARLIST = [ str(v) for v in Ordered_DICT]
    var=VARLIST[0]
    VarObj= Ordered_DICT[var]
    nStations, jpk =VarObj.shape
    D.close()
    return VARLIST, nStations, jpk

def dumptxtfile(outfile, HovMatrix, TL, iP):
    dateformat="%Y%m%d"
    limit_levels=(~np.isnan(HovMatrix[0,iP,:])).sum()
    depth = TheMask.zlevels[:limit_levels]
    depth.resize(limit_levels,1)

    fid = open(outfile,'w')
    fid.write(" \t")
    np.savetxt(fid,depth.T, '%10.5f\t',newline="m\n")
    for iFrame in range(TL.nTimes):
        fid.write(TL.Timelist[iFrame].strftime(dateformat) + "\t")
        np.savetxt(fid,HovMatrix[iFrame,iP,:limit_levels], fmt="%10.5f\t",newline="")
        fid.write("\n")
    fid.close()

MeasPoints = read_Positions_for_Pointprofiles(args.pointlist)
FrameDesc   =""
Stations    =""
 


for i in TL.filelist        : FrameDesc  +=str(i).split('.')[1] + ", "
for i in MeasPoints['Name'] : Stations   +=str(i)               + ", "



VARLIST, nStations, jpk =get_info(TL.filelist[0])

for var in VARLIST[rank::nranks]:
    outfile = OUTDIR + var + ".pkl"
    TIMESERIES=np.zeros((nFrames,nStations,jpk),dtype=np.float32)
    
    for iFrame, filename in enumerate(TL.filelist):
        A = netcdf4.readfile(filename, var)
        A[A==0]=np.nan
        TIMESERIES[iFrame,:,:] = A
        
    L = [TIMESERIES,TL]
    fid = open(outfile,"wb")
    pickle.dump(L, fid) 
    fid.close()
    ncOUT = netCDF4.Dataset( OUTDIR + var + ".nc","w")
    ncOUT.createDimension('nFrames',nFrames)
    ncOUT.createDimension('nStations', nStations)
    ncOUT.createDimension('depth', jpk)
    
    
    ncvar=ncOUT.createVariable(var,'f',('nFrames','nStations','depth'))
    ncvar[:] =TIMESERIES

    setattr(ncOUT,"frame_list"  ,  FrameDesc)
    setattr(ncOUT,"sub___list"  ,  Stations[:-2])

    ncOUT.close()
    nStations = len(MeasPoints)
    for iP in range(nStations):
        station_name=MeasPoints[iP]['Name']
        outfile="%stxt/%s_%s.txt" %(OUTDIR,var,station_name)
        print(outfile)
        dumptxtfile(outfile, TIMESERIES, TL, iP)

