import argparse
from xml.dom import minidom
def argument():
    parser = argparse.ArgumentParser(description = '''
    Parses xml file looking for Ingested and Validated attribute.
    If they are both True, returns "validated", else does not return anything.
    
    ''',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(   '--inputfile', '-i',
                                type = str,
                                required = True,
                                help = '''path of the input file''')

    return parser.parse_args()
args = argument()


filename=args.inputfile

xmldoc = minidom.parse(filename)
Ingested=str(xmldoc.getElementsByTagName("Delivery")[0].getAttributeNode("Ingested").value)
Validated=str(xmldoc.getElementsByTagName("Delivery")[0].getAttributeNode("Validated").value)

if ((Ingested=="True") & (Validated=="True")):
    print "validated"

