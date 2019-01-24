import argparse

def argument():
    parser = argparse.ArgumentParser(description = 'Executes tar -tf in parallel')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required=True,
                                help = 'path of dir with tar files')

    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                required =True,
                                help = 'path of dir with untared files')
    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "*.tar",
                                help = 'list of tar files')
    return parser.parse_args()

args=argument()
import os,sys
import glob

def file2stringlist(filename):
    LIST=[]
    filein=file(filename)
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


INPUT_DIR = addsep(args.inputdir)
OUTPUTDIR = addsep(args.outputdir)
fileLIST  = glob.glob(INPUT_DIR + args.filelist)

os.chdir(OUTPUTDIR)

for tarfile in fileLIST[rank::nranks]: 

    command= "tar -xf " + tarfile 
    print command
    os.system(command)
