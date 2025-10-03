import os,glob
from subprocess import Popen,PIPE
import datetime

def shell_hash(fpath, method='md5sum'):
    if not os.path.isfile(fpath):
        return ''
    cmd = [method, fpath] #delete shlex
    p = Popen(cmd, stdout=PIPE)
    output, _ = p.communicate()
    if p.returncode:
        return ''
    output = output.split()
    #return output[-1]# mac version
    return output[0]
logfile="/marconi/home/usera07ogs/a07ogs00/OPA/V3C/log/20180109/opa.marconi.002.opa_put.out"

PROD_DIR="/marconi/home/usera07ogs/a07ogs00/OPA/V3C/wrkdir/2/POSTPROC/PRODUCTS/"

DATASETS={"sv04-med-ogs-bio-an-fc-d":"BIOL", 
          "sv04-med-ogs-car-an-fc-d":"CARB", 
          "sv04-med-ogs-nut-an-fc-d":"NUTR",
          "sv04-med-ogs-pft-an-fc-d":"PFTC"}

LINES=[]
LINES.append("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
LINES.append("<delivery product=\"MEDSEA_ANALYSIS_FORECAST_BIO_006_014\" PushingEntity=\"BIO_PU\" date=\"20180109T092700Z\">\n")


for dataset in DATASETS.keys():

    LINES.append("<dataset DatasetName=\"" + dataset + "\" >\n")
    FILELIST=glob.glob(PROD_DIR + "*" + DATASETS[dataset] +"*")
    FILELIST.sort()
    
    for filename in FILELIST:
        basename=os.path.basename(filename)
        md5sum = shell_hash(filename)
        #command = "grep PrEx %s | grep %s | grep -v du-bu | awk '{print $2}'"  %(logfile, basename)
        command = ["/marconi_scratch/usera07ogs/a07ogs01/PROD_V4C/prodotti/get_times.sh", basename]
        p = Popen(command, stdout=PIPE)
        output, _ = p.communicate()
        timestrings=output.rsplit("\n")
        st=datetime.datetime.strptime(timestrings[0],"%Y%m%d-%H:%M:%S")
        et=datetime.datetime.strptime(timestrings[1],"%Y%m%d-%H:%M:%S")

        
        StartUploadTime=st.strftime("%Y%m%d%H%M%SZ") 
        StopUploadTime =et.strftime("%Y%m%d%H%M%SZ") 
        line="<file FileName=\"%s\" StartUploadTime=\"%s\" StopUploadTime=\"%s\"  Checksum=\"%s\" FinalStatus=\"Delivered\"> \n"  %(basename,StartUploadTime,StopUploadTime,md5sum)


        LINES.append(line)
        LINES.append("</file>\n")
    
    LINES.append("</dataset>\n")



LINES.append("</delivery>\n")

fid=open("myDNT.xml","w")
fid.writelines(LINES)
fid.close()