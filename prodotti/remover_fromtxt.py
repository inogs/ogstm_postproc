import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates xml file for removing forecasts.
    Ouput file name is imposed
    Input file comes from copernicusmarine client
    echo n | copernicusmarine get -i cmems_mod_med_bgc-car_anfc_4.2km_P1D-m  --filter "*202312*d-OGS*" --show-outputnames | grep fc-sv08 | grep INFO

    ''')
    parser.add_argument(   '--inputfile', '-i',
                                type = str,
                                required = True,
                                help = '')
    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = '')

    return parser.parse_args()

args = argument()


from commons.utils import file2stringlist
from datetime import datetime
from commons.utils import addsep

filename=args.inputfile
OUTDIR=addsep(args.outdir)

PRODUCT_ID="MEDSEA_ANALYSISFORECAST_BGC_006_014"
PushingEntity="MED-OGS-TRIESTE-IT"
DntTime=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

DNT_FILE="%s_%s.xml" %(PRODUCT_ID, DntTime)

LINES = file2stringlist(filename)
line=LINES[0]
iStart=line.find("cmems_mod")
iEnd=line.find("/", iStart)
dataset=line[iStart:iEnd]

OUTLINES=[]
OUTLINES.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
OUTLINES.append("<delivery product=\"%s\" PushingEntity=\"%s\" date=\"%s\">"  %(PRODUCT_ID,PushingEntity,DntTime))
OUTLINES.append("  <dataset DatasetName=\"%s\">" % (dataset))



for line in LINES:
    iStart=line.find("cmems_mod")
    iEnd=line.find("/", iStart)
    dataset=line[iStart:iEnd]
    filename=line[iEnd+1:]

    OUTLINES.append("<file Filename=\"%s\" > <KeyWord>Delete</KeyWord> </file> " %(filename))
    #print(dataset, filename)
    
OUTLINES.append("  </dataset>")    
OUTLINES.append("</delivery>")



outfile=OUTDIR + "MEDSEA_ANALYSISFORECAST_BGC_006_014_" + DntTime + ".xml"

fid=open(outfile,'wt')
for line in OUTLINES:
    fid.write(line + "\n")
fid.close()

print("Dumping deletion lines in " + outfile)