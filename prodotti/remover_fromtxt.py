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


from bitsea.commons.utils import file2stringlist
from datetime import datetime
from bitsea.commons.utils import addsep

filename=args.inputfile
OUTDIR=addsep(args.outdir)


PushingEntity="MED-OGS-TRIESTE-IT"
DntTime=datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")



LINES = file2stringlist(filename)

if len(LINES)==0:
    print(filename + " is empty. Exit")
    import sys
    sys.exit()

line=LINES[0]
iStart=line.find("MEDSEA")
iEnd=line.find("/", iStart)
PRODUCT_ID=line[iStart:iEnd]
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

    OUTLINES.append("<file FileName=\"%s\" > <KeyWord>Delete</KeyWord> </file> " %(filename))
    #print(dataset, filename)
    
OUTLINES.append("  </dataset>")    
OUTLINES.append("</delivery>")



outfile= "%s%s_%s.xml" %(OUTDIR, PRODUCT_ID, DntTime)

fid=open(outfile,'wt')
for line in OUTLINES:
    fid.write(line + "\n")
fid.close()

print("Dumping deletion lines in " + outfile)
