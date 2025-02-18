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
    parser.add_argument(   '--timeaverage', '-t',
                                type = str,
                                required = True,
                                choices = ['monday','tuesday','thursday','friday'],
                                )
    parser.add_argument(   '--var', '-v',
                                type = str,
                                required = True,
                                help = ''' var name'''
                                )

    return parser.parse_args()


args = argument()




from bitsea.commons.Timelist import TimeList
from bitsea.commons.mask import Mask
from bitsea.commons.time_averagers import TimeAverager3D, TimeAverager2D
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
TheMask = Mask.from_file(args.maskfile)
var=args.var

VARLIST=['kd490']


TL=TimeList.fromfilenames(None, INPUTDIR, "ave*nc", filtervar=var)
if args.timeaverage == 'monday'  : WEEKLY_REQS=TL.getWeeklyList(1)
if args.timeaverage == 'tuesday' : WEEKLY_REQS=TL.getWeeklyList(2)
if args.timeaverage == 'thursday': WEEKLY_REQS=TL.getWeeklyList(4)
if args.timeaverage == 'friday'  : WEEKLY_REQS=TL.getWeeklyList(5)



for req in WEEKLY_REQS[rank::nranks]:
    indexes,weights=TL.select(req)

    outfile = OUTPUTDIR + "ave." + req.string + "-12:00:00." + var + ".nc"
    print(outfile)
    filelist=[]
    for k in indexes:
        t = TL.Timelist[k]
        filename = INPUTDIR + "ave." + t.strftime("%Y%m%d-%H:%M:%S") + "." + var + ".nc"
        filelist.append(filename)
    M3d = TimeAverager3D(filelist, weights, var, TheMask)
    netcdf4.write_3d_file(M3d, var, outfile, TheMask)

