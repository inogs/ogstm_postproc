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
    parser.add_argument(   '--product', '-p',
                                type = str,
                                required = True,
                                help = '')
    parser.add_argument(   '--dataset', '-d',
                                type = str,
                                required = True,
                                help = '')
    parser.add_argument(   '--version', '-v',
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

PRODUCT_ID=args.product
dataset=args.dataset
version=args.version

OUTLINES=[]
OUTLINES.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>")
OUTLINES.append("<delivery product=\"%s\" PushingEntity=\"%s\" date=\"%s\">"  %(PRODUCT_ID,PushingEntity,DntTime))
OUTLINES.append("  <dataset DatasetName=\"%s_%s\">" % (dataset, version))


for line in LINES:
    if len(line)>0:
        yyyy=line[0:4]
        mm=line[4:6]
        if dataset.endswith("P1D-m"):
            filename=f"{yyyy}/{mm}/{line}"
        else:
            filename=f"{yyyy}/{line}"
        OUTLINES.append("    <file FileName=\"%s\" > <KeyWord>Delete</KeyWord> </file> " %(filename))

    
OUTLINES.append("  </dataset>")    
OUTLINES.append("</delivery>")



outfile= "%s%s_%s.xml" %(OUTDIR, PRODUCT_ID, DntTime)

fid=open(outfile,'wt')
for line in OUTLINES:
    fid.write(line + "\n")
fid.close()

print("Dumping deletion lines in " + outfile)
