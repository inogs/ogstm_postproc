import os
import glob
import argparse

def argument():
    parser = argparse.ArgumentParser(description = 'Executes gzip in parallel')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help = 'The directory containing uncompressed files')

    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                required = True,
                                help = 'The directory where you want to dump compressed files')

    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "ave*N1p.nc",
                                help = 'ave*.N1p.nc') 
    parser.add_argument(   '--erase',"-e",
                                dest = 'erase',
                                default = "none",
                                action = 'store_true',
                                help = 'deletes original files')
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
ZIPPEDdir = addsep(args.outputdir)
PATH_NAME = args.filelist

os.chdir(INPUT_DIR)
fileLIST = glob.glob(PATH_NAME)
fileLIST.sort()

for avefile in fileLIST[rank::nranks]: 
    zipped = ZIPPEDdir + os.path.basename(avefile) + ".gz"
    if args.erase:
        command= "gzip -c " + avefile + " > " + zipped + "; [[ $?==0 ]] && rm -f " + avefile
        os.system(command)
    else:
        #if os.path.exists(zipped): continue
        command= "gzip -c " + avefile + " > " + zipped    
        os.system(command)


    

    