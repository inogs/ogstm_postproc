from commons.time_interval import TimeInterval
from commons.Timelist import TimeList

IonamesFile="/gpfs/work/IscrC_MYMEDBIO/COPERNICUS/bit.sea/postproc/IOnames.xml"
MODELDIR="/pico/scratch/userexternal/gbolzon0/TRANSITION/wrkdir/MODEL/AVE_FREQ_1/"
TI=TimeInterval('20140101','20150101','%Y%m%d')
TL = TimeList.fromfilenames(TI, MODELDIR,"ave*N1p.nc",IonamesFile)
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

