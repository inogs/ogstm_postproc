import os,sys
import glob
import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
          Executes time average in parallel 
          of monthly files provided by CLIMA_100 simulations
          Here, files have name like : MFSMEDSEA_1d_20000101_20000131_grid_T.nc
          It generates files with name like : T20000101-00:00:00.nc
                      ''')
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required=True,
                                help = '/gpfs/scratch/userexternal/gbolzon0/CLIMA_100/4.5/MONTHLY_UNZIPPED/')

    parser.add_argument(   '--outputdir', '-o',
                                type = str,
                                required=True,
                                help = '/gpfs/scratch/userexternal/gbolzon0/CLIMA_100/4.5/MONTHLY_UNZIPPED/')


    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "*nc",
                                help = 'T*nc') 
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
OUTDIR    =addsep(args.outputdir)
PATH_NAME = args.filelist

os.chdir(INPUT_DIR)
fileLIST = glob.glob(PATH_NAME)
fileLIST.sort()

# monthly_file="MFSMEDSEA_1d_20000101_20000131_grid_T.nc"
for monthly_file in fileLIST[rank::nranks]:
    basename=os.path.basename(monthly_file)
    ndays=int(basename[28:30])
    var= basename[36]
    date8 = basename[13:21]
    monthly_ave_file = OUTDIR + var + date8 + "-00:00:00.nc"
    command= "ncra -d time_counter,0,%d %s -O %s" %(ndays, monthly_file, monthly_ave_file)    
    os.system(command)
    

    

    
