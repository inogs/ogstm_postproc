from xml.dom import minidom


xmldoc = minidom.parse('OpecDescriptor.xml')

prefix = str(xmldoc.getElementsByTagName("prefix")[0].attributes["string"].value)

NODE=xmldoc.getElementsByTagName("weekly")[0].getElementsByTagName("native")
WEEKLY_NATIVE_NODES=NODE[0].getElementsByTagName("dataset")

for n in WEEKLY_NATIVE_NODES:
    longname    = n.attributes['long_name'].value
    units       = n.attributes['units'].value
    outfile     = n.attributes['file'].value
    outvarname  = n.attributes['OPECname']
    Mod_varname = n.attributes['ogstm_varname']
    

WEEKLY_AGG_NODES=xmldoc.getElementsByTagName("weekly")[0].getElementsByTagName("aggregate")[0].getElementsByTagName("aggvar")
for aggnode in WEEKLY_AGG_NODES:
    longname   =  aggnode.attributes['long_name'].value
    units      =  aggnode.attributes['units'].value
    outfile    =  aggnode.attributes['file'].value
    outvarname =  aggnode.attributes['OPECname']
    
