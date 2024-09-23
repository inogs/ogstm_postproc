import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Dump profiles on text files
    ''',
    formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(   '--outdir', '-o',
                            type = str,
                            required =True,
                            default = "./",
                            help = ''' Output dir'''
                            )
    parser.add_argument(   '--inputfile', '-i',
                            type = str,
                            required =True,
                            default = "profiler",
                            help = '''pkl input file'''
                            )
    parser.add_argument(   '--maskfile', '-m',
                            type = str,
                            required =True,
                            default = "mask",
                            help = '''maskfile'''
                            )

    parser.add_argument(   '--variable', '-v',
                            type = str,
                            required =False,
                            default = "var",
                            help = '''var name'''
                            )
    parser.add_argument(   '--coastness', '-c',
                            type = int,
                            required =False,
                            default = "0",
                            help = '''index of coastness to select in the pkl matrix'''
                            )
    parser.add_argument(   '--basin', '-b',
                            type = int,
                            required =False,
                            default = "0",
                            help = '''index of the basin to select in the pkl matrix'''
                            )
    parser.add_argument(   '--statistic', '-s',
                            type = int,
                            required =False,
                            default = "0",
                            help = '''index of the statistic to select in the pkl matrix'''
                            )



    return parser.parse_args()

args = argument()

from bitsea.commons.utils import addsep
from bitsea.timeseries.plot import read_pickle_file
from bitsea.commons.Timelist import TimeList,TimeInterval
from bitsea.commons.mask import Mask
import numpy as np



OUTDIR = addsep(args.outdir)
COAST = args.coastness
BASIN = args.basin
STAT = args.statistic
INPUTFILE = args.inputfile
MASK_file = args.maskfile
VAR = args.variable

TheMask=Mask(MASK_file)
z_levels = TheMask.zlevels

PKL_values,PKL_TL = read_pickle_file(INPUTFILE)
number_of_levels = (~np.isnan(PKL_values[0,BASIN,COAST,:,STAT])).sum()

fid = open (OUTDIR+VAR+"profile.txt",'wt')

for time in range(PKL_TL.nTimes) :
    t1=PKL_TL.Timelist[time]
    date=t1.strftime('%Y-%m-%d 00:00:00')
    fid.write("%s\t%d\t%d\n" %(date,number_of_levels,2))
    for idz in range(number_of_levels):
        fid.write("%f\t%f\n" %(-z_levels[idz],PKL_values[time,BASIN,COAST,idz,STAT]))

fid.close()    
