import numpy as np
import scipy.io.netcdf as NC
import read_opec_descriptor
import os,glob



jpi = 362
jpj = 128
jpk = 72
file0="/gpfs/scratch/userexternal/ateruzzi/OPA_872_RA13-R02/wrkdir/20130108/RST_after.20130108-12:00:00.nc"
NCaf = NC.netcdf_file(file0,'r')
AFTER=NCaf.variables['P1i'].data.copy()
NCaf.close()
tmask = AFTER<1e+19; 

def getData(filename, varlist):
    NCin = NC.netcdf_file(filename,"r")
    if len(varlist)==1:
        M=NCin.variables[varlist[0]].data.copy()
    else:
        M=np.zeros((jpk,jpj,jpi), np.float32)
        for var in varlist:
            Junk= NCin.variables[var].data.copy()
            M += Junk          
    return M

def dumpfile(outfile, varname, M):    
    ncOUT= NC.netcdf_file(outfile,"w")
    ncOUT.createDimension("longitude",     jpi)
    ncOUT.createDimension("latitude" ,     jpj)
    ncOUT.createDimension("depth"    ,     jpk) 
       
    ncvar=ncOUT.createVariable(varname , 'f', ('depth','latitude','longitude'))
    setattr(ncvar,'_FillValue'    ,        1.e+20)
    setattr(ncvar,'missing_value' ,        1.e+20)
    ncvar[:] = M
    ncOUT.close()
    print outfile



    

BASEDIR="/gpfs/scratch/userexternal/ateruzzi/OPA_872_RA13-R02/wrkdir/"

DIRLIST=glob.glob(BASEDIR + "2013*")

for DIR in DIRLIST:
    DATE=os.path.basename(DIR) #"20130108"


    DIR       = BASEDIR + DATE +  "/"
    RST_after = DIR + "RST_after." + DATE + "-12:00:00.nc"
    RSTbefore = DIR + "RSTbefore." + DATE + "-12:00:00.nc"
        
    for n in read_opec_descriptor.WEEKLY_NATIVE_NODES:
        var = str(n.attributes['ogstm_varname'].value)
        outfile = DIR  + 'norm_innovation.' + var + ".nc"
        
        AFTER  = getData(RST_after,[var])
        BEFORE = getData(RSTbefore,[var])    
        
        NORM_INNOVATION=(AFTER-BEFORE)/BEFORE
        NORM_INNOVATION[~tmask]=1.e+20
        dumpfile(outfile,var,NORM_INNOVATION)
        
        
    for aggnode in read_opec_descriptor.WEEKLY_AGG_NODES:
        outvarname = str(aggnode.attributes['long_name'].value)
        outfile    = DIR + 'norm_innovation.' + outvarname + ".nc"
        nodes = aggnode.getElementsByTagName("ogstm_var")
        agglist=[]
        for node in nodes: agglist.append(str(node.attributes['name'].value))
        
        AFTER  = getData(RST_after,agglist)
        BEFORE = getData(RSTbefore,agglist)
        
        NORM_INNOVATION=(AFTER-BEFORE)/BEFORE
        NORM_INNOVATION[~tmask]=1.e+20
        dumpfile(outfile,outvarname,NORM_INNOVATION)







