import os,sys
import glob
import argparse

def argument():
    parser = argparse.ArgumentParser(description = 'Executes tar in parallel')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                default = None,
                                help = '/plx/userogs/ogstsf79/OPA/V4-dev/wrkdir/2/MODEL/AVE_FREQ_1/')

    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                default = None,
                                help = '/plx/userogs/ogstsf79/OPA/V4-dev/wrkdir/2/MODEL/AVE_FREQ_1/')


    parser.add_argument(   '--varlist',"-v",
                                type = str,
                                required=True,
                                help = 'varlistfile') 
    return parser.parse_args()


def file2stringlist(filename):
    LIST=[]
    filein=open(filename)
    for line in filein:
        LIST.append(line[:-1])
    filein.close()
    return LIST

def addsep(string):    
    if string[-1] != os.sep:
        return string + os.sep
    else:
        return  string 

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


args = argument()
INPUT_DIR = addsep(args.inputdir)
TARdir = addsep(args.outputdir)
VARLIST=file2stringlist(args.varlist)
os.chdir(INPUT_DIR)





for var in VARLIST[rank::nranks]: 
    tarfile  =  TARdir + var + ".tar"

    command= "tar -cf " + tarfile + "   *" + var + "*"
    print(command)
    os.system(command)
