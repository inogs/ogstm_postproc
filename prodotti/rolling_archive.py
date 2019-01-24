import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Prints the name of product file that DU should delete
   ''',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--productfile', '-p',
                                type = str,
                                required = True,
                                help =''
                                )
    
    parser.add_argument(   '--group',"-g",
                                type = str,
                                required = True,
                                help = '')

    parser.add_argument(    '--rundate',"-d", 
                                type = str,
                                required = True,
                                help = '''rundate of previous run''' )
    parser.add_argument(    '--archive_dir',"-a", 
                                type = str,
                                required = True,
                                help = '''Chain archive directory, e.g. /pico/home/usera07ogs/a07ogs00/OPA/V4/archive''' )
    
    return parser.parse_args()
args = argument()



from datetime import datetime
from dateutil.relativedelta import relativedelta
import os,glob
from commons.utils import addsep
tr='d' #daily
def V3_1_filename(timeobj,FGroup, bulletin_date,DType): 
    return timeobj.strftime('%Y%m%d_') + tr + "-OGS--" + FGroup + "-MedBFM2-MED-b" + bulletin_date +"_" + DType + "-sv03.00.nc"


today=datetime.strptime(args.rundate,'%Y%m%d')
bulletin_date=today.strftime("%Y%m%d")
ARCHIVE_DIR=addsep(args.archive_dir)
FGROUPS = ['NUTR', 'PFTC', 'BIOL', 'CARB']
FGroup = FGROUPS[0]

if today.isoweekday() == 2 : last_run = today - relativedelta(days=4)
if today.isoweekday() == 5 : last_run = today - relativedelta(days=3)
lastrun_dir=ARCHIVE_DIR + last_run.strftime("%Y%m%d/POSTPROC/AVE_FREQ_1/PRODUCTS/")




def get_last_file_from_files(today_file,lastrun_dir,FGroup):
    timestr=today_file[:8]
    filelist=glob.glob(lastrun_dir + timestr +"*" + FGroup + "*")
    if len(filelist)==1:
        basename=os.path.basename(filelist[0])
        filename=timestr[:4] + "/" + timestr[4:6] + "/" + basename
        return filename
    if len(filelist)==0: return None
    if len(filelist)>1 :
        raise EnvironmentError
   





print get_last_file_from_files(args.productfile, lastrun_dir, args.group)

    
    
    
