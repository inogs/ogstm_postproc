import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates 4 seasonal images for each variable
    with subbasin errorbar.
    Each errorbar has:
    - a line for percentiles 10-90
    - a box for percentiles 25-75
    - a star for percentile 50
    
    Kz is plotted in two layers.
    Examples in 
    https://medeaf.inogs.it/internal-validation/Benchmark/PHYS/

    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = 'percentiles dir')
    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = '/some/path/')
    parser.add_argument(   '--runname', '-n',
                                type = str,
                                required = True,
                                help = 'benchmark')

    return parser.parse_args()

args = argument()


import numpy as np
import matplotlib
matplotlib.use('Agg')
import pylab as pl
from basins import V2 as OGS
from commons import season
from commons.utils import addsep
from commons.layer import Layer


color='b'
INPUTDIR=addsep(args.inputdir)
RunName = args.runname
OUTPUTDIR=addsep(args.outdir)


SUBlist = OGS.P.basin_list
nSub = len(SUBlist)
X=np.arange(nSub)
e=0.1
S = season.season()


#VARLIST=["mld", "stratification_index", "KE_total", "KE_ratio"]
#UNITS = ['m', ' ', 'm4/s2', ' ']
VARLIST=['dcm','cm','WLB','DOM','OM','phosphocline','nitracline','nitracline_th2','P_l','N3n','N1p','O2o','ppn']
UNITS = ['m','mmol/m$^3$','m','m','mmol/m$^3$','m','m','m','mg /m$^3$','mmol/m$^3$','mmol/m$^3$','mmol/m$^3$','g C/m$^3$']

VARLIST=['dcm','phosphocline','nitracline','nitracline_th','P_l','N3n','N1p','O2o']
UNITS = ['m','m','m','m','mg /m$^3$','mmol/m$^3$','mmol/m$^3$','mmol/m$^3$']

#UNITS = ['m','mmol/m^3','m','m','mmol/m^3','m','m','m','mg /m^3','mmol/m^3','mmol/m^3','mmol/m^3','g C/m^3']
for iSeas in range(4):
#for iSeas in [0,2,3]:
    for ivar, var in enumerate(VARLIST):
        outfile = "%s%s_Percentiles.%s.png" %(OUTPUTDIR,var, S.SEASON_LIST_NAME[iSeas])
        fig,ax=pl.subplots(1,1)
        fig.set_size_inches(15,5)
        inputfile= "%sPercentiles.%d.%s.npy" %(INPUTDIR, iSeas, var)
        P=np.load(inputfile)
        for isub in range(nSub):
            p1, p5,  p10, p25, p50, p75, p90, p95, p99 = P[:,isub]
            x = isub
            if isub == 0: 
                ax.plot([x,x],[ p10,p90 ], color, label=RunName)
            else:
                ax.plot([x,x],[ p10,p90 ], color)
            ymin, ymax = p25, p75
            ax.plot([x-e, x+e, x+e, x-e, x-e], [ymin, ymin, ymax, ymax, ymin] , color)
            ax.plot(x,p50,'*', color=color)
        ax.legend()
        ax.grid(True)
        ax.set_xticks(X)
        subnames=[sub.name for sub in OGS.P]
        ax.set_xticklabels(subnames)
        ax.set_ylabel(var + " " + UNITS[ivar])

        fig.suptitle(var + " Percentiles " + S.SEASON_LIST_NAME[iSeas])
        fig.savefig(outfile)
        pl.close(fig)
