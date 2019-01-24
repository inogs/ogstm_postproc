#script to calculate time series of fluxes

import glob

#import os,sys

import pickle


from mydtype import *

#import scipy.io.netcdf as NC
import netCDF4
import numpy as np

#import matplotlib.pyplot as plt


def flux_across_transect(VAR,datadir):
    
    fid = open('/marconi_scratch/userexternal/ggalli00/CLIMA_100/TR-PO4-O2-R7c/preproc/FLUXES/Matrices.pkl','rb'); Matrices = pickle.load(fid); fid.close()
        
    nTrans=len(Matrices)
        
    LISTAFILE=glob.glob(datadir +"/"+"flux*.nc")

    LISTAFILE.sort()
    
    nFiles=len(LISTAFILE) #(nFiles = 1559 for T6)
    
    d0in = netCDF4.Dataset(LISTAFILE[0],"r")
    
    index =  np.array(d0in.variables['index'])
    print index.shape
    d0in.close()
    
        
    #PREALLOCATE SOLUTION STUFF
    FaT={} #fluxes across transects
    for tr in range(nTrans):
        FaT[tr] = np.zeros([Matrices[tr].shape[0], Matrices[tr].shape[1], nFiles], dtype=flux_dt)
            
  
    # loop on files, each one a month
    #for i in range(1):
    for i in range(nFiles):
   
        # import fluxes
        din = netCDF4.Dataset(LISTAFILE[i],"r")
        d=np.array(din.variables[VAR]) #Second entry 1:adv-u; 2: adv-v; 3: adv-w; 4:sed-w; 5:hdf-x; 6:hdf-y; 7:zdf-z
        din.close()        
        
        
        for tr in range(nTrans):
            
            B=Matrices[tr].copy()
            
            FLX=np.zeros(B.shape, dtype=flux_dt)
            FLX[:][:,:]=np.NAN
           
            #print FLX 
            for lin in range(B.shape[0]):
                for col in range(B.shape[1]):
                    
                    # rescale from mmol/s to Mmol/y 
                    if B[lin, col] > 0:
                        FLX[:][lin, col] = d[ np.where( index == B[lin, col] ), :]* 86400*365/1.e+9
                    
            FaT[tr][:,:,i]=FLX         
            del FLX # per sicurezza
           
    
    
    #time dependendent flux across transects 
    
    Results = {}
    
    Results['ALB']  =   FaT[0]['adv-u'] + FaT[0]['hdf-x']
    Results['AEG1'] =   FaT[1]['adv-u'] + FaT[1]['hdf-x']
    Results['AEG2'] =   FaT[2]['adv-v'] + FaT[2]['hdf-y']
    Results['AEG3'] = - FaT[3]['adv-u'] - FaT[3]['hdf-x']
    Results['ADR']  =   FaT[4]['adv-v'] + FaT[4]['hdf-y']
    Results['SIC1'] =   FaT[5]['adv-u'] + FaT[5]['hdf-x']
    Results['SIC2'] = - FaT[6]['adv-v'] - FaT[6]['hdf-y']    
    
    
    # dump results
    transects = ['ALB','AEG1','AEG2','AEG3','ADR','SIC1','SIC2']
    
    for trx in transects:
        fname = trx + '_' + VAR + '_2D_flux.npy'
        fid = open(fname, 'wb')
        np.save(fid, Results[trx])
        fid.close()

    print 'Calculation done!'
    
