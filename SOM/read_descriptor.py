from xml.dom import minidom

xmldoc = minidom.parse('VarDescriptor.xml')
# To Do: read namelist.passivetrc (ctrcnm) and namelist.diagnostics(dia)

NATIVE_VARS=set()

NODE=xmldoc.getElementsByTagName("vars_for_All_Statistics")[0].getElementsByTagName("native")
VARNODES=NODE[0].getElementsByTagName("var")
for n in VARNODES:
    NATIVE_VARS.add( str(n.attributes['name'].value) )

print len(NATIVE_VARS), "native vars"


AGGR_VARS=[]
NODE=xmldoc.getElementsByTagName("vars_for_All_Statistics")[0].getElementsByTagName("aggregate")
VARNODES=NODE[0].getElementsByTagName("var")
for n in VARNODES:
    AGGR_VARS.append(str(n.attributes['name'].value))
print len(AGGR_VARS), " vars which we aggregate"



SOME_VARS=set()    
NODE=xmldoc.getElementsByTagName("var_for_Some_Statistics")
VARNODES=NODE[0].getElementsByTagName("var")
for n in VARNODES:
    SOME_VARS.add( str(n.attributes['name'].value) )
print len(SOME_VARS), " vars for Some Statistics"

repeatition=SOME_VARS.intersection(NATIVE_VARS)
for i in repeatition :
    print "**** removing", i , "from var_for_Some_Statistics" 
    SOME_VARS.remove(i)



LIST_To_Online_PostPROC = NATIVE_VARS.union(SOME_VARS).union(set(AGGR_VARS))  # ottengo la longlist, senza ripetizione

print len(LIST_To_Online_PostPROC), "variables for online postproc"


F=file('longlist',"w")
for line in LIST_To_Online_PostPROC:
    F.write(line + "\n")
F.close()

ARCHIVE_VARS=[]
NODE=xmldoc.getElementsByTagName("toArchive")
VARNODES=NODE[0].getElementsByTagName("var")
for n in VARNODES:
    ARCHIVE_VARS.append( str(n.attributes['name'].value) )

SET_ARCHIVE_VARS=set(ARCHIVE_VARS)


if len(SET_ARCHIVE_VARS) != len(ARCHIVE_VARS):
    print "duplication in toArchive vars"
    for var in SET_ARCHIVE_VARS:
        if ARCHIVE_VARS.count(var) > 1 :
            print var, "is duplicated. REMOVE it from xml descriptor ***************"

F=file('varStoredInAve',"w")
for line in ARCHIVE_VARS:
    F.write(line + "\n")
F.close()

AGGREGATE_DICT={}
AGGVARNODES=xmldoc.getElementsByTagName("vars_for_All_Statistics")[0].getElementsByTagName("aggregate")[0].getElementsByTagName("aggvar")
for NODE in AGGVARNODES:
    aggvar=str(NODE.attributes['name'].value)
    
    N=NODE.getElementsByTagName("var")
    L=[]
    for n in N:
        L.append( str(n.attributes['name'].value))
    AGGREGATE_DICT[aggvar]=L
