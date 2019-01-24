import scipy.io.netcdf as NC
import glob
import os,sys
import numpy as np
from maskload import *
from read_descriptor import AGGREGATE_DICT, SOME_VARS, NATIVE_VARS
import datetime

try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1
# su fermi 7 minuti 1 ave

def Integrals_mask(Conc, Weight):

    Weight_sum      = Weight.sum()
    Mass            = (Conc * Weight).sum()
    Weighted_Mean   = Mass/Weight_sum        


    return Statistics

def region_name(v):
    for i in range(len(v)):
        if v[i]:
            return SUBlist[i] 
    return 'error'
  


BASEDIR = os.getenv("CINECA_SCRATCH") + "/" + os.getenv("OPA_HOME") + "/wrkdir/SOM-ANALYSIS/"
INPUT_AVEDIR    = BASEDIR + "DATA/"
OUTPUT_DIR_INT  = BASEDIR + 'INTEGRALS/'
OUTPUT_DIR_MPR  = BASEDIR + 'STAT_PROFILES/'
OUTPUT_DIR_PRO  = BASEDIR + 'PROFILES/'


for DIR in [OUTPUT_DIR_INT, OUTPUT_DIR_MPR, OUTPUT_DIR_PRO]:
    os.system("mkdir -p " + DIR)


aveLIST = glob.glob(INPUT_AVEDIR +sys.argv[1]) #"ave*nc"
aveLIST.sort()

nframe = len(aveLIST)

nvar   = len(NATIVE_VARS) + len(AGGREGATE_DICT)

Lon1d  = Lon[mask200_2D]
Lat1d  = Lat[mask200_2D]
SUB1d  = SUB[0,mask200_2D]
npoints= Lon1d.shape[0]

NORM     = sum(dZ[0:tk_1,:,:])
INT_NORM = NORM[mask200_2D]

all_matrix=np.zeros((nframe,nvar,npoints),np.float32)

for avefile in aveLIST[rank::nranks]:    

    month  = int(os.path.basename(avefile)[4:6])

    print avefile

    ncIN  = NC.netcdf_file(avefile,"r")

    var_c = 0

    for var in list(NATIVE_VARS):
        VAR        = ncIN.variables[var].data[0,:,:,:]      
        dVAR       = VAR*dZ
        INT        = sum(dVAR[0:tk_1,:,:]) 
        INT_mask   = INT[mask200_2D]/INT_NORM
        all_matrix[month-1,var_c,:]=INT_mask  
        var_c=var_c+1
        

    for outvar in AGGREGATE_DICT.keys():
        localvars=AGGREGATE_DICT[outvar]
        VAR = np.zeros((jpk,jpj,jpi),np.float32)
        for var in localvars:
            VAR+=ncIN.variables[var].data[0,:,:,:]
        dVAR       = VAR*dZ
        INT        = sum(dVAR[0:tk_1,:,:])
        INT_mask   = INT[mask200_2D]/INT_NORM
        all_matrix[month-1,var_c,:]=INT_mask  

# Writing header of the File
fileout= os.getenv("OPA_HOME") + '.txt'
F = file(fileout, 'wb')

header ='#n' 

for var in list(NATIVE_VARS):
    for avefile in aveLIST[rank::nranks]:    
        header = header + '\t' + var + os.path.basename(avefile)[4:6]

for var in AGGREGATE_DICT.keys():
    for avefile in aveLIST[rank::nranks]:    
        header = header + '\t' + var + os.path.basename(avefile)[4:6]

header = header + '\n'
F.write("%s " %header)     
header ='#l\t' + 'lon\t' + 'lat\t' + 'region'
header = header + '\n'
F.write("%s " %header)     
# Writing samples

for np in range(npoints): 
    if region_name(SUB1d[np]) != 'error':
        for var in range(nvar):
            for frame in range(nframe):
                F.write("%g\t" %all_matrix[frame,var,np])
        F.write("%g\t" %Lon1d[np])
        F.write("%g\t" %Lat1d[np])
        F.write("%s"  %region_name(SUB1d[np]))
        F.write("\n")

# End

F.close()
