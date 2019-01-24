import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates COPERNICUS products files from reanalysis.
    Product name = MEDSEA_REANALYSIS_BIO_006_008.
    Standard names are choose from
    http://cfconventions.org/Data/cf-standard-names/30/build/cf-standard-name-table.html.


   Files have been checked from http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl.

   Parallel executable, can be called by mpirun.
                               ''',
                               formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help ='The directory wrkdir/MODEL/AVE_FREQ_2/ where reanalysis has run.'
                                )
    parser.add_argument(   '--outputdir',"-o",
                                type = str,
                                required = True,
                                help = 'Path of existing dir')
    parser.add_argument(    '--time',"-t", 
                                type = str,
                                required = True,
                                help = '''Path of input text file with the yyyymmdd list''' )
    parser.add_argument(    '--maskfile', "-m",
                                type = str,
                                required = True,
                                help = '''Path for the maskfile ''')
        
    return parser.parse_args()


args = argument()
import netCDF4
import scipy.io.netcdf as NC
import numpy as np
import datetime,os
from commons.utils import addsep, file2stringlist
from commons.mask import Mask


try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1


INPUTDIR  = addsep(args.inputdir)
OUTPUTDIR = addsep(args.outputdir)
TIMELIST   = file2stringlist(args.time)


bulletin_date = "20190115"
DType="re"
tr='m' #monthly mean


cut = 52 #1/12
#cut = 80 #1/24
maskfile = args.maskfile
TheMask = Mask(maskfile,ylevelsmatvar="gphit", xlevelsmatvar="glamt")
jpk, jpj, jpi = TheMask.shape
nav_lev = TheMask.zlevels
Lon = TheMask.xlevels[0,:].astype(np.float32)
Lat = TheMask.ylevels[:,0].astype(np.float32)
tmask = TheMask.mask
tmask.resize(1,jpk,jpj,jpi)
Lon = Lon[cut:]
tmask = tmask[:,:,:,cut:]



FGROUPS = ['NUTR', 'PFTC', 'BIOL', 'CARB']

bulletin_type='analysis'
bulletin_time = datetime.datetime.strptime(bulletin_date,"%Y%m%d")


def readfile(filename,var):

    ncIN = netCDF4.Dataset(filename,'r')
    M = np.array(ncIN.variables[var])
    ncIN.close()
    return M[:,:,:,cut:]

def readdata(time, var):
    '''time is a date17 string'''
    
    inputfile = INPUTDIR + "ave."  + time + "." + var + ".nc"
    return readfile(inputfile,var)

def create_Structure(filename):
    ref=  'Please check in CMEMS catalogue the INFO section for product MEDSEA_ANALYSIS_FORECAST_BIO_006_008 - http://marine.copernicus.eu/'
    inst  ='OGS (Istituto Nazionale di Oceanografia e di Geofisica Sperimentale) , Sgonico (Trieste) - Italy'
    ncOUT = netCDF4.Dataset(filename,"w",format="NETCDF4")
    ncOUT.createDimension('longitude', jpi-cut)
    ncOUT.createDimension('latitude' ,jpj)
    ncOUT.createDimension('depth'    ,jpk)
    ncOUT.createDimension('time'     ,  1)
    
    setattr(ncOUT,'Conventions'  ,'CF-1.0' )
    setattr(ncOUT,'references'   , ref     )
    setattr(ncOUT,'institution'  , inst    )
    setattr(ncOUT,'source'       , '3DVAR-OGSTM-BFM')
    setattr(ncOUT,'comment'      , ref)
    setattr(ncOUT,'contact'      ,'servicedesk.cmems@mercator-ocean.eu')
    setattr(ncOUT,'bulletin_date', bulletin_time.strftime("%Y-%m-%d") )
    setattr(ncOUT,'bulletin_type', bulletin_type)
    setattr(ncOUT,'field_type'   , 'monthly_mean_beginning_at_time_field')
    
    basename = os.path.basename(filename)
    timestr = basename[:6] + "01-00:00:00" # 01 of every month
    D = datetime.datetime.strptime(timestr,'%Y%m%d-%H:%M:%S')
    Dref = datetime.datetime(1970,1,1,0,0,0)
    Diff = D-Dref
    
    ncvar = ncOUT.createVariable('time','d',('time',))
    setattr(ncvar,'units',       'seconds since 1970-01-01 00:00:00')
    setattr(ncvar,'long_name'    ,'time')
    setattr(ncvar,'standard_name','time')
    setattr(ncvar,'axis'         ,'T')
    setattr(ncvar,'calendar'     ,'standard')
    ncvar[:] = Diff.days*3600*24 + Diff.seconds
    

    ncvar = ncOUT.createVariable('depth'   ,'f', ('depth',))
    setattr(ncvar,'units'        ,'m')
    setattr(ncvar,'long_name'    ,'depth')
    setattr(ncvar,'standard_name','depth')
    setattr(ncvar,'positive'     ,'down')
    setattr(ncvar,'axis'         ,'Z')
    setattr(ncvar,'valid_min'    ,nav_lev.min())
    setattr(ncvar,'valid_max'    ,nav_lev.max())
    ncvar[:] = nav_lev
    
    ncvar = ncOUT.createVariable('latitude','f' ,('latitude',))
    setattr(ncvar, 'units'        ,'degrees_north')
    setattr(ncvar,'long_name'    ,'latitude')
    setattr(ncvar,'standard_name','latitude')
    setattr(ncvar, 'axis'         ,'Y')
    setattr(ncvar,'valid_min'    , Lat.min())
    setattr(ncvar, 'valid_max'    ,Lat.max())
    ncvar[:]=Lat

    ncvar = ncOUT.createVariable('longitude','f',('longitude',))
    setattr(ncvar, 'units'        ,'degrees_east')
    setattr(ncvar,'long_name'    ,'longitude')
    setattr(ncvar, 'standard_name','longitude')
    setattr(ncvar, 'axis'         ,'X')
    setattr(ncvar, 'valid_min'    , Lon.min())
    setattr(ncvar, 'valid_max'    , Lon.max())
    ncvar[:]=Lon
    
    
    return ncOUT
    
def V2_filename(timeobj,FGroup):
    return timeobj.strftime('%Y%m') + "01_" + tr + "-OGS--" + FGroup + "-ogstm_bfm4-MED-b" + bulletin_date +"_" + DType + "-fv06.00.nc"
def V3_filename(timeobj,FGroup):    
    return timeobj.strftime('%Y%m01_') + tr + "-OGS--" + FGroup + "-MedBFM1-MED-b" + bulletin_date +"_" + DType + "-sv04.10.nc"
def V3_1_filename(timeobj,FGroup):    
    return timeobj.strftime('%Y%m%d_') + tr + "-OGS--" + FGroup + "-MedBFM2-MED-b" + bulletin_date +"_" + DType + "-sv03.00.nc"


for timestr in TIMELIST[rank::nranks]:
    timeobj = datetime.datetime.strptime(timestr,"%Y%m%d-%H:%M:%S")
    for FGroup in FGROUPS:
        product_file = V3_filename(timeobj, FGroup)
        print "rank =", rank, product_file
        ncOUT = create_Structure(OUTPUTDIR + product_file)
        
        
        if FGroup == 'NUTR':
            setattr(ncOUT,'title','Nitrate and Phosphate (3D) - Monthly Mean')
            
            ncvar = ncOUT.createVariable('nit', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'millimol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Nitrate in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_nitrate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "N3n")
            ncvar[:] = M
            
            
            ncvar = ncOUT.createVariable('pho', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'millimol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Phosphate in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_phosphate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            
            M = readdata(timestr, "N1p")
            ncvar[:] = M
        
        if FGroup == 'PFTC':
            setattr(ncOUT,'title','Carbon and Chlorophyll content of phytoplankton functional type(3D) - Monthly Mean')

            ncvar = ncOUT.createVariable('pcb', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3')
            setattr(ncvar,'long_name'    ,'Concentration of Phytoplankton Biomass in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_phytoplankton_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            P1c = readdata(timestr, "P1c")
            P2c = readdata(timestr, "P2c")
            P3c = readdata(timestr, "P3c")
            P4c = readdata(timestr, "P4c")
            pcb = (P1c + P2c + P3c +P4c)*(1./12.)*(0.001) 
            #CONVERSION from "mgC m-3" to "molC m-3"
            # conversion factor: 1/12 * 10-3
            pcb[~tmask] = 1.e+20
            ncvar[:] = pcb
            
            ncvar = ncOUT.createVariable('chl', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'milligram m-3')
            setattr(ncvar,'long_name'    ,'Concentration of Chlorophyll in sea water')
            setattr(ncvar,'standard_name','concentration_of_chlorophyll_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            P1l = readdata(timestr, "P1l")
            P2l = readdata(timestr, "P2l")
            P3l = readdata(timestr, "P3l")
            P4l = readdata(timestr, "P4l")
            chl = (P1l + P2l + P3l +P4l)
            chl[~tmask] = 1.e+20
            ncvar[:] = chl
            
        if FGroup == 'BIOL':
            setattr(ncOUT, 'title', "Net Primary Production and Dissolved Oxygen (3D) - Monthly Mean")
            
            ncvar = ncOUT.createVariable('dox', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'millimol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Dissolved Molecular Oxygen in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_dissolved_molecular_oxygen_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            O2o = readdata(timestr,"O2o")
            ncvar[:] = O2o
            
            ncvar = ncOUT.createVariable('ppn', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3 s-1')
            setattr(ncvar,'long_name'    ,'Net Primary Production in sea water')
            setattr(ncvar,'standard_name','tendency_of_mole_concentration_of_particulate_organic_matter_expressed_as_carbon_in_sea_water_due_to_net_primary_production')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ppn = readdata(timestr,"ppn")
            ppn = ppn*(1./12.)*(0.001)*(1./86400.)      # CONVERSION from "mgC day-1 m-3" to "molC s-1 m-3" 
                                                # conversion factor: 1/12 * 10-3 * 1/86400
            ppn[~tmask] = 1.e+20
            ncvar[:] = ppn
            
        if FGroup == 'CARB':
            setattr(ncOUT, 'title',"Ocean pCO2 and Ocean Acidity (3D) - Monthly Mean")
            
            ncvar = ncOUT.createVariable('pco', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'Pa')
            setattr(ncvar,'long_name'    ,'ocean_pco2_expresses_as_carbon_dioxide_partial_pressure')
            setattr(ncvar,'standard_name','surface_partial_pressure_of_carbon_dioxide_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            pco = readdata(timestr, "pCO2")
            ncvar[:] = pco
            
            ncvar = ncOUT.createVariable('ph', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'1')
            setattr(ncvar,'long_name'    ,'PH')
            setattr(ncvar,'standard_name','sea_water_ph_reported_on_total_scale')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ph = readdata(timestr, "PH")
            ncvar[:] =ph
    
        ncOUT.close()
        
