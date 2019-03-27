import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates timelist_a and timelist_s files
    ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = '/some/path/MODEL/AVE_FREQ_1/')

    return parser.parse_args()

args = argument()
from commons.Timelist import TimeList
from commons.utils import addsep

MODELDIR=addsep(args.inputdir)

TL = TimeList.fromfilenames(None, MODELDIR,"ave*N1p.nc")
ANALYSIS_DAYS  =[]
SIMULATION_DAYS=[]
for time in TL.Timelist:
    line=time.strftime('%Y%m%d')+"\n"
    if time.isoweekday() == 2: 
        ANALYSIS_DAYS.append(line)
    else:
        SIMULATION_DAYS.append(line)

F=open('timelist_a','w')
F.writelines(ANALYSIS_DAYS)
F.close()

F=open('timelist_s','w')
F.writelines(SIMULATION_DAYS)
F.close()
