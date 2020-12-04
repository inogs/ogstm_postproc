import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates the monthly climatology from STAT_PROFILES
    Reads from pkl file, dumps results in another one 
    
    ''')
    parser.add_argument(   '--inputfile', '-i',
                                type = str,
                                required = True,
                                help = 'input pkl file')

    parser.add_argument(   '--outfile', '-o',
                                type = str,
                                required = True,
                                help = 'output pkl file'
                                )
    parser.add_argument(   '--year', '-y',
                                type = str,
                                required = False,
                                default = 2000,
                                help = 'ideal year for clim values'
                                )

    return parser.parse_args()

args = argument()

import numpy as np
from commons import timerequestors
from timeseries.plot import read_pickle_file
from commons import genUserDateList as DL
from commons.Timelist import TimeList
import pickle

dataIN,TL=read_pickle_file(args.inputfile)

nFrames,nSub,nCoast,nLev,nStat=dataIN.shape
dataOUT=np.zeros((12,nSub,nCoast,nLev,nStat),np.float32)


for imonth in range(12):
    req=timerequestors.Clim_month(imonth+1)
    ii,w=TL.select(req)
    dataOUT[imonth,:]=dataIN[ii,:].mean(axis=0)

year=2000
datestart=str(year)+"0101-00:00:00"
dateend  =str(year)+"1201-00:00:00"
datelist=DL.getTimeList(datestart, dateend, "months=1")

L=[dataOUT, TimeList(datelist)]

fid = open(args.outfile,"wb")
pickle.dump(L, fid) 
fid.close()

