import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates monthly averaged files
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = ''' '''

                                )

    parser.add_argument(   '--maskfile', '-m',
                                type = str,
                                required = True,
                                help = ''' mask filename .'''
                                )

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = ''' output directory'''
                                )
    parser.add_argument(   '--var', '-v',
                                type = str,
                                required = True,
                                help = ''' model var name'''
                                )
    return parser.parse_args()


args = argument()


from bitsea.commons.Timelist import TimeList, TimeInterval
from bitsea.commons import timerequestors
from bitsea.commons.mask import Mask
from bitsea.commons.time_averagers import TimeAverager3D_std, TimeAverager2D_std
from bitsea.commons import netcdf4
from bitsea.commons.utils import addsep

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


INPUTDIR=addsep(args.inputdir)
OUTPUTDIR=addsep(args.outdir)

TheMask=Mask(args.maskfile)
var = args.var

TI= TimeInterval('1999','2020', '%Y')
TL=TimeList.fromfilenames(TI, INPUTDIR, "ave*.nc", filtervar=var)

MONTHS=range(1,13)
for month in MONTHS[rank::nranks]:
    req = timerequestors.Clim_month(month)
    
    indexes,weights=TL.select(req)

    if len(indexes)==0: continue
    inputvar=var

    outfile = OUTPUTDIR + "ave.2000" + req.string + "01-00:00:00." + var + ".nc"
    print(outfile,flush=True)
    filelist=[]
    for k in indexes:
        t = TL.Timelist[k]
        filename = INPUTDIR + "ave." + t.strftime("%Y%m%d-%H:%M:%S") + "." + inputvar + ".nc"
        filelist.append(filename)
    for i in filelist: print(i)
    if netcdf4.dimfile(filename, var)==3:
        M3d,std = TimeAverager3D_std(filelist, weights, inputvar, TheMask)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask)
        std[~TheMask.mask] = 1.e+20
        netcdf4.write_3d_file(std, var +"_std", outfile, TheMask)
    else:
        M2d,std = TimeAverager2D_std(filelist, weights, inputvar, TheMask)
        netcdf4.write_2d_file(M2d, var, outfile, TheMask)
        std[~TheMask.mask_at_level(0)] = 1.e+20
        netcdf4.write_2d_file(std, var + "_std", outfile, TheMask)
        
        