import argparse


def argument():
    parser = argparse.ArgumentParser("Generates an ordered time list")
    parser.add_argument(   '--datestart',"-s",
                                type = str,
                                required = True,
                                help = '20120101-12:00:00')
    parser.add_argument(   '--dateend',"-e",
                                type = str,
                                required = True,
                                help = '20120110-12:00:00')
    parser.add_argument(   '--days',
                                type = int,
                                required = False,
                                help = '')
    parser.add_argument(   '--hours',
                                type = int,
                                required = False,
                                help = '')
    parser.add_argument(   '--min',
                                type = int,
                                required = False,
                                help = '')
    parser.add_argument(   '--months',
                                type = int,
                                required = False,
                                help = '')
    parser.add_argument(   '--dateformat',
                                type = str,
                                required = False,
                                default = '%Y%m%d-%H:%M:%S')
    
    
    return parser.parse_args()

args = argument()
from bitsea.commons import genUserDateList as DL
if args.days  : TL   = DL.getTimeList(args.datestart, args.dateend, days  = args.days   )
if args.hours : TL   = DL.getTimeList(args.datestart, args.dateend, hours = args.hours  )
if args.min   : TL   = DL.getTimeList(args.datestart, args.dateend, minutes  = args.min )
if args.months: TL   = DL.getTimeList(args.datestart, args.dateend, months = args.months)


#dateFormat=""
for t in TL:
    print(t.strftime(args.dateformat))

