
from commons import genUserDateList as DL
from datetime import datetime

d1=datetime(2016,11,29,12)
dateformat="%Y%m%d-%H:%M:%S"
ds = DL.getTimeList(d1.strftime(dateformat), d1.strftime(dateformat), "days=1")

fid = open('timelist.a','w')
fid.writelines([t.strftime(dateformat + "\n") for t in ds])
fid.close()

d2 = d1 + DL.relativedelta(days=1)
d3 = d1 + DL.relativedelta(days=6)
ds = DL.getTimeList(d2.strftime(dateformat), d3.strftime(dateformat), "days=1")
fid = open('timelist.s','w')
fid.writelines([t.strftime(dateformat + "\n") for t in ds])
fid.close()



d4 = d1 + DL.relativedelta(days=7)
d5 = d1 + DL.relativedelta(days=16)
ds = DL.getTimeList(d4.strftime(dateformat), d5.strftime(dateformat), "days=1")
fid = open('timelist.f','w')
fid.writelines([t.strftime(dateformat + "\n") for t in ds])
fid.close()
