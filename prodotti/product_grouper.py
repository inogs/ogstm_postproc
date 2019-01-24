from commons.timeseries import TimeSeries
from commons.time_interval import TimeInterval
from commons.utils import addsep

starttime="20170901"
end__time="20180601"
LOC = "/marconi_scratch/usera07ogs/a07ogs01/new-DU/V3C/"
archive_dir="/marconi/home/usera07ogs/a07ogs00/OPA/V3C/archive/"

TI=TimeInterval(starttime,end__time,'%Y%m%d')

TS = TimeSeries(TI, archive_dir,postfix_dir='POSTPROC/AVE_FREQ_1/PRODUCTS/',glob_pattern="*sm*")
TS.extract_analysis(LOC, command="cp $INFILE $OUTFILE", remove_ext=False)