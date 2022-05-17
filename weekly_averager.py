import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates weekly averaged files
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

    return parser.parse_args()


args = argument()




from commons.Timelist import TimeList
from commons.mask import Mask
from commons.time_averagers import TimeAverager3D, TimeAverager2D
from commons import netcdf4
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
OUTPUTDIR=addsep(args.outdir)
TheMask = Mask(args.maskfile)

VARLIST=['kd490']


TL=TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar="kd490")

WEEKLY_REQS = TL.getWeeklyList(1)


for req in WEEKLY_REQS[rank::nranks]:
    indexes,weights=TL.select(req)
    for var in VARLIST:
        if var=='pH': 
            inputvar='PH'
        else:
            inputvar=var
        outfile = OUTPUTDIR + "ave." + req.string + "-12:00:00." + var + ".nc"
        print(outfile)
        filelist=[]
        for k in indexes:
            t = TL.Timelist[k]
            filename = INPUTDIR + "ave." + t.strftime("%Y%m%d-%H:%M:%S") + "." + inputvar + ".nc"
            filelist.append(filename)
        M3d = TimeAverager3D(filelist, weights, inputvar, TheMask)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask)

