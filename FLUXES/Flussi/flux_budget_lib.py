# script to calculate time series of fluxes

import glob

import os,sys

import pickle

from maskload import nav_lev, getDepthIndex

from mydtype import *

import scipy.io.netcdf as NC
import netCDF4
import numpy as np


def dumpfile(filename,listafile,val):
    F=file(filename,"w")    
    datelen=-12 # [-3 -> yyyymmdd-hh:mm:ss date],[-12 ->  yyyymmdd]
    t=0    
    for i in val :
        yyyymmdd=listafile[t][-20:datelen]
        yyyy=yyyymmdd[0:4]
        mm  =yyyymmdd[4:6]
        dd  =yyyymmdd[6:8]
        xmdate=yyyy  + mm +  dd
#        xmdate=yyyy + '-' + mm + '-' + dd
        F.write(" %s " %xmdate ); t=t+1
        F.write(" %8.5e " %i )
        F.write("\n") 
    F.close()

def getDepthIndex(nav_lev, lev_mask):
    jk_m = 0
    for jk in range(nav_lev.__len__()):
        if nav_lev[jk] < lev_mask:
            jk_m = jk
    return jk_m

def isInDepthRange(matrices, dStart,dEnd):
    
    output      = matrices.copy()
    output[:,:] = 0
    
    k1=getDepthIndex(nav_lev, dStart)
    k2=getDepthIndex(nav_lev, dEnd)
    
    if ( k2-k1 < 0):
        print 'Warning: check depth definition'
        return 0
    
    k2=min(output.shape[0],k2)
    
    output[k1:k2,:] = 1
    
    print 'dStart-->', dStart,'k1-->',k1
    print 'dEnd---->', dEnd  ,'k2-->',k2
    
    return output

def flux_budget(VAR,dStart,dEnd,datadir):
    
#VAR='N1p'

#dStart= 0  
#dEnd  = 5000 
# Dati di input
#datadir='/Users/plazzari/Documents/workspace/Paolo_TOOLS/FLUXES/TRANSECTS/DATA'

    p=[]
    
    fid = open('/gpfs/scratch/userexternal/plazzari/eas_v12/preproc_master/FLUXES/Matrices.pkl','rb'); Matrices = pickle.load(fid); fid.close()
    
    fid = open('/gpfs/scratch/userexternal/plazzari/eas_v12/preproc_master/FLUXES/rINV.pkl','rb');     rINV     = pickle.load(fid); fid.close()
    
    nTrans=len(Matrices)
    
    FLUXFILE='/gpfs/scratch/userexternal/plazzari/eas_v12/preproc_master/FLUXES/Fluxes.nc'
    
    LISTAFILE=glob.glob(datadir +"/"+"flux*.nc")
    
    nFiles=len(LISTAFILE)
    
    dintegral=np.zeros((nTrans,nFiles),dtype=flux_dt)
    
#    d0in = NC.netcdf_file(FLUXFILE,"r")
    d0in = netCDF4.Dataset(LISTAFILE[0],"r")
    
    index =  np.array(d0in.variables['index'])
    print index.shape
    d0in.close()
    
    for tr in range(nTrans):
        
        A=Matrices[tr].copy()
        
        B=A*isInDepthRange(A, dStart, dEnd)
            
        idx=np.in1d(index,B.ravel())
        
        p.append(idx.nonzero()[:][0])
    
    for i in range(nFiles):
        
#        print 'Opening file....' + LISTAFILE[i]
        din = netCDF4.Dataset(LISTAFILE[i],"r")
        
        d=np.array(din.variables[VAR]) #Second entry 1:adv-u; 2: adv-v; 3: adv-w; 4:sed-w; 5:hdf-x; 6:hdf-y; 7:zdf-z
        
        din.close()
        
        for tr in range(nTrans):
        
            aux=d[p[tr],:].copy()
    
    # spatial integral over the transect along index

#           aux2 = aux.sum(axis=0) * 1800*12/1.e+9 # data rescaled Mmol/year Multiplication bt time step --> 1800 s and conversion to Mmol -->/1.e+9
            aux2 = aux.sum(axis=0) * 86400*365/1.e+9
            dintegral[tr,i]=np.array(tuple(aux2),flux_dt)
            
    flux=dintegral.copy()
    
    #time dependendent flux across transects
    
    ALB =  flux['adv-u'][0,:] + flux['hdf-x'][0,:]
    AEG =( flux['adv-u'][1,:] + flux['hdf-x'][1,:] ) + ( flux['adv-v'][2,:] + flux['hdf-y'][2,:]) - ( flux['adv-u'][3,:] + flux['hdf-x'][3,:])
    ADR=   flux['adv-v'][4,:] + flux['hdf-y'][4,:]
    SIC= ( flux['adv-u'][5,:] + flux['hdf-x'][5,:] ) - ( flux['adv-v'][6,:] + flux['hdf-y'][6,:])
    
    #average flux across transects
    
    ALBm=ALB.mean();print 'ALB', VAR, 'average -->', ALBm
    AEGm=AEG.mean();print 'AEG', VAR, 'average -->', AEGm
    ADRm=ADR.mean();print 'ADR', VAR, 'average -->', ADRm
    SICm=SIC.mean();print 'SIC', VAR, 'average -->', SICm
    
    # dump results
    
    filename='ALB_L1_' + str(dStart) + '_L2_' + str(dEnd) + '_' + VAR + '_flux.dat' ; dumpfile(filename, LISTAFILE, ALB)
    filename='AEG_L1_' + str(dStart) + '_L2_' + str(dEnd) + '_' + VAR + '_flux.dat' ; dumpfile(filename, LISTAFILE, AEG)
    filename='ADR_L1_' + str(dStart) + '_L2_' + str(dEnd) + '_' + VAR + '_flux.dat' ; dumpfile(filename, LISTAFILE, ADR)
    filename='SIC_L1_' + str(dStart) + '_L2_' + str(dEnd) + '_' + VAR + '_flux.dat' ; dumpfile(filename, LISTAFILE, SIC)
    print 'Calculation done!'
