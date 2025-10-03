import argparse


def argument():
    parser = argparse.ArgumentParser("Generates an ordered time list")
    parser.add_argument(   '--year',"-y",
                                type = str,
                                required = True,
                                help = '2012')
    parser.add_argument(   '--month',"-m",
                                type = str,
                                required = True,
                                help = '01')    
   
    
    
    return parser.parse_args()

args = argument()
from bitsea.commons import genUserDateList as DL
from datetime import datetime
from dateutil.relativedelta import relativedelta
datestart = datetime(int(args.year), int(args.month), 1)
date__end = datestart + relativedelta(months=1)

dateFormat="%Y%m%d-%H:%M:%S"



TL   = DL.getTimeList(datestart.strftime(dateFormat), date__end.strftime(dateFormat), days = 1 )
dateFormat="%Y%m%d"

for t in TL[:-1]:
    print(t.strftime(dateFormat))
