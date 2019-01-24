import os,sys
import glob
import argparse

def argument():
    parser = argparse.ArgumentParser(description = 'Executes gunzip in parallel')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required=True,
                                help = '/plx/userogs/ogstsf79/OPA/V4-dev/wrkdir/2/MODEL/AVE_FREQ_1/')

    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                required=True,
                                help = '/plx/userogs/ogstsf79/OPA/V4-dev/wrkdir/2/MODEL/AVE_FREQ_1/')


    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "ave*N1p.nc",
                                help = 'ave*.N1p.nc') 
    parser.set_defaults(erase=False) 
    return parser.parse_args()

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
UNZIPPEDdir=addsep(args.outputdir)
PATH_NAME = args.filelist

os.chdir(INPUT_DIR)
fileLIST = glob.glob(PATH_NAME)
fileLIST.sort()

for zipped in fileLIST[rank::nranks]: 
    unzipped = UNZIPPEDdir + os.path.basename(zipped)[:-3]
    command= "gzip -dc " + zipped + " > " + unzipped    
    os.system(command)
    

    

    
