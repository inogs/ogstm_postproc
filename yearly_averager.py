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

from commons.Timelist import TimeList, TimeInterval
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

TheMask=Mask(args.maskfile)
var = args.var

TI= TimeInterval('1999','2020', '%Y')
TL=TimeList.fromfilenames(TI, INPUTDIR, "ave*.nc", filtervar=var)
YEARLY_REQS=TL.getYearlist()


for req in YEARLY_REQS[rank::nranks]:
    indexes,weights=TL.select(req)

    inputvar=var

    outfile = OUTPUTDIR + "ave." + req.string + "0101-00:00:00." + var + ".nc"
    print outfile
    filelist=[]
    for k in indexes:
        t = TL.Timelist[k]
        filename = INPUTDIR + "ave." + t.strftime("%Y%m%d-%H:%M:%S") + "." + inputvar + ".nc"
        filelist.append(filename)
    if netcdf4.dimfile(filename, var)==3:
        M3d = TimeAverager3D(filelist, weights, inputvar, TheMask)
        netcdf4.write_3d_file(M3d, var, outfile, TheMask)
    else:
        M2d = TimeAverager2D(filelist, weights, inputvar, TheMask)
        netcdf4.write_2d_file(M2d, var, outfile, TheMask)
