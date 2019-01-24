from commons import netcdf4
import numpy as np
import glob



def read_flux_file(filename,var, Transect_Matrices, dtype, index=None):
    '''Returns:
    * FLUX_LIST * A list of numpy ndarrays 
                  one for each matrix in Transect_Matrices
                  with the dtype provided as argument
                   
    '''
    if index is None:
        index = netcdf4.readfile(filename,'index')

    d = netcdf4.readfile(filename, var)
    FLUX_LIST=[]
    for ib, B in enumerate(Transect_Matrices):
        nrows, ncols  = B.shape        
        FLX=np.zeros((nrows,ncols), dtype=dtype)
        FLX[:][:,:]=np.NAN
        for lin in range(nrows):
            for col in range(ncols):
                    if B[lin, col] > 0:
                        pos=np.where( index == B[lin, col] )[0][0]
                        FLX[lin, col] = np.array(tuple(d[pos,:]),dtype)
        FLUX_LIST.append(FLX)
    return FLUX_LIST


def read_flux_timeseries(filelist, var, Transect_Matrices, dtype):
    '''
    Returns:
    * Fluxes_across_Transects * a list of 3D ndarrays (nrows, ncols, nFrames) 
                                where fluxes across a transect can be found as
                                Fluxes_across_Transects[iTrans][:,:,iFrame][dtype_field]
    
    '''

    nFrames=len(filelist)
    index = netcdf4.readfile(filelist[0],'index')
    nTrans = len(Transect_Matrices)
    
    #PREALLOCATE SOLUTION STUFF
    FaT=[] #fluxes across transects
    for itr, B in enumerate(Transect_Matrices):
        nrows, ncols  = B.shape
        FaT.append (np.zeros((nrows,ncols, nFrames), dtype=dtype))

    for iFrame, filename in enumerate(filelist):
        file_flux = read_flux_file(filename, var, Transect_Matrices, dtype, index)
        for itr in range(nTrans):
            FaT[itr][:,:,iFrame] = file_flux[itr]
    return FaT


def flux_two_timeseries(Flux_matrix):
    '''
    Argument:
    * Flux_Matrix * a 3D ndarray (nrows, ncols, nFrames) 
    
    Returns:
    * OUT * an ndarray (nFrames,2) such as:
            Positive=OUT[:,0], timeseries of integral of positive flux
            Negative=OUT[:,1], timeseries of integral of negative flux, with (-) sign.    
    '''

    _,_ , nFrames = Flux_matrix.shape
    ii =np.isnan(Flux_matrix)
    Flux_matrix[ii] = 0
    OUT = np.zeros((nFrames,2), np.float32) #dtype=[('positive',np.float32), ('negative', np.float32)])

    for iframe in range(nFrames):
        m = Flux_matrix[:,:,iframe]
        positive = m>0
        OUT[iframe,0] = m[ positive].sum()
        OUT[iframe,1] = m[~positive].sum()

    return OUT
        
   
def flux_hovmoeller(Flux_matrix):
    nrows,_ , nFrames = Flux_matrix.shape
    ii =np.isnan(Flux_matrix)
    Flux_matrix[ii] = 0
    Hov_matrix = np.zeros((nrows,nFrames),np.float32)
    for iframe in range(nFrames):
        m = Flux_matrix[:,:,iframe]
        Hov_matrix[:,iframe] = m.sum(axis=1)
    return Hov_matrix
        
    

if __name__ == "__main__":
    import pickle
    flux_dt =np.dtype([('adv-u',np.float),('adv-v',np.float),('adv-w',np.float),('sed-w',np.float),\
                       ('hdf-x',np.float),('hdf-y',np.float),('zdf-z',np.float)])
    Matrices_file="/gpfs/work/OGS18_PRACE_P_0/OPEN_BOUNDARY/preproc_Fluxes/FLUXES/Matrices.pkl"
    fid = open(Matrices_file,'rb'); Matrices = pickle.load(fid); fid.close()
    filename = '/gpfs/work/OGS18_PRACE_P_0/OPEN_BOUNDARY/wrkdir/MODEL/FLUXES/flux.20170101-04:30:00.nc'
    INPUTDIR  ="/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_01/wrkdir/MODEL/FLUXES"
    #Matrices=[Matrices[-1]]
    A = read_flux_file(filename, "N1p", Matrices, flux_dt)
    LISTAFILE=glob.glob(INPUTDIR +"/"+"flux*.nc")
    LISTAFILE.sort()
    flux = read_flux_timeseries(LISTAFILE,"N1p",Matrices,flux_dt)
    for itr in range(len(Matrices)):
        X = flux[itr]['adv-u'] + flux[itr]['hdf-x']
        balance =flux_two_timeseries(X)
        S = flux_hovmoeller(X)
    AEG_hov = flux_hovmoeller( flux[1]['adv-u'] + flux[1]['hdf-x']) + \
              flux_hovmoeller( flux[2]['adv-v'] + flux[2]['hdf-y']) - \
              flux_hovmoeller( flux[3]['adv-u'] + flux[3]['hdf-x'])
    balance = flux_two_timeseries( flux[1]['adv-u'] + flux[1]['hdf-x']) + \
              flux_two_timeseries( flux[2]['adv-v'] + flux[2]['hdf-y']) - \
              flux_two_timeseries( flux[3]['adv-u'] + flux[3]['hdf-x'])
