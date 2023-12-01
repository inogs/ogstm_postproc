import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates xml file for removing forecasts.
    Ouput file name is imposed
    Hypothesis: input file has only uploads, no deletions.

    ''')
    parser.add_argument(   '--inputfile', '-i',
                                type = str,
                                required = True,
                                help = 'MEDSEA_ANALYSISFORECAST_BGC_006_014_20231130T083952Z.xml')


    return parser.parse_args()

args = argument()

from xml.dom import minidom
from datetime import datetime

xmldoc = minidom.parse(args.inputfile)


NODES=xmldoc.getElementsByTagName("file")
dataset_node=xmldoc.getElementsByTagName("dataset")[0]
delivery_node=xmldoc.getElementsByTagName("delivery")[0]


for node in NODES:
    filename=node.getAttribute('FileName')
    if filename.find('sm')>0: dataset_node.removeChild(node)
    node.removeAttribute('StartUploadTime')
    node.removeAttribute('StopUploadTime')
    node.removeAttribute('Checksum')
    node.removeAttribute('FinalStatus')
    K = xmldoc.createElement("Keyword")
    node.appendChild(K)
    text = xmldoc.createTextNode('Delete')
    K.appendChild(text)
    
d=datetime.utcnow()
timestr=d.strftime('%Y%m%d%H%M%SZ')

delivery_node.setAttribute('date',timestr)

outfile="MEDSEA_ANALYSISFORECAST_BGC_006_014_" + timestr + ".xml"

fid=open(outfile,'wt')
fid.write(xmldoc.toxml())
fid.close()
#xmldoc.toxml()
#print(xmldoc.toprettyxml(indent='\t'))
