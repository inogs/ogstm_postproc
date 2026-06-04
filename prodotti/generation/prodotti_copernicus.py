import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
   Creates COPERNICUS products files from chain.
   Product name = MEDSEA_ANALYSISFORECAST_BGC_006_014
   Standard names are choose from
   http://cfconventions.org/Data/cf-standard-names/30/build/cf-standard-name-table.html.

   Files have been checked from http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl.
   Requirements from:[AD8] CMEMS Interface Requirement PU-MDS V2.6.pdf available at
   https://mercatoroceanfr.sharepoint.com/sites/COP2TechnicalWG/Documents partages/General/Applicable Documents/[AD8] CMEMS Interface Requirement PU-MDS V2.6.pdf

   Parallel executable, can be called by mpirun.
   ''',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--inputdir', '-i',
                                type = str,
                                required = True,
                                help ='The directory wrkdir/MODEL/AVE_FREQ_1/ where chain has run.'
                                )

    parser.add_argument(   '--outputdir',"-o",
                                type = str,
                                required = True,
                                help = 'Path of existing dir')

    parser.add_argument(    '--time',"-t", 
                                type = str,
                                required = True,
                                help = '''Path of input text file with the yyyymmdd list''' )
    parser.add_argument(    '--DType',"-d", 
                                type = str,
                                required = True,
                                help = '''Analysis, simulation , or forecast''',
                                choices = ["an","sm","fc"])
     
    parser.add_argument(    '--bulltime',"-b",
                                type = str,
                                required = True,
                                help = '''The bulletin time a string time in the format yyyymmdd ''')
    parser.add_argument(    '--maskfile', "-m",
                                type = str,
                                required = True,
                                help = '''Path for the maskfile ''')
    parser.add_argument(    '--tr',
                                type = str,
                                required = True,
                                choices = ["daily","monthly"])

    return parser.parse_args()


args = argument()

import netCDF4
import numpy as np
import datetime,os
from bitsea.commons.utils import addsep, file2stringlist
from bitsea.commons.mask import Mask
from bitsea.commons.dataextractor_open import DataExtractor

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
TIMELIST  = file2stringlist(args.time)
DType     = args.DType
bulletin_date = args.bulltime
maskfile = args.maskfile
if args.tr=='daily'  :
    tr='d'
    field_type='daily_mean_centered_at_time_field'
if args.tr=='monthly':
    tr='m'
    assert args.DType=='an'
    field_type='monthly_mean_beginning_at_time_field'

cut = 80 #1/24
TheMask = Mask.from_file(maskfile, ylevels_var_name="gphit", xlevels_var_name="glamt")
jpk, jpj, jpi = TheMask.shape
nav_lev = TheMask.zlevels
Lon = TheMask.xlevels[0,:].astype(np.float32)
Lat = TheMask.ylevels[:,0].astype(np.float32)
tmask = TheMask.mask

Lon = Lon[cut:]
tmask = tmask[:,:,cut:]

FGROUPS = ['NUTR', 'PFTC', 'BIOL', 'CARB','CO2F','EXCO']

if DType == "an": 
    bulletin_type='analysis'
    StatusFlag = 0
if DType == "sm": 
    bulletin_type='simulation'
    StatusFlag = 1
if DType == "fc": 
    bulletin_type='forecast'
    StatusFlag = 1

bulletin_time = datetime.datetime.strptime(bulletin_date,"%Y%m%d")

def readfile(filename,var,ndims):
    M=DataExtractor(TheMask,filename,var, dimvar=ndims).values
    if ndims==3:return M[:,:,cut:]
    if ndims==2:return M[:,cut:]

def readdata(time, var, ndims=3):
    
    inputfile = INPUTDIR + "ave."  + time + "-12:00:00." + var + ".nc"
    return readfile(inputfile,var,ndims=ndims)

def create_Structure(filename, fgroup):
    ref=  'Please check in CMEMS catalogue the INFO section for product MEDSEA_ANALYSISFORECAST_BGC_006_014 - https://marine.copernicus.eu/'
    inst  ='OGS (Istituto Nazionale di Oceanografia e di Geofisica Sperimentale) , Sgonico (Trieste) - Italy'
    ncOUT = netCDF4.Dataset(filename,"w",format="NETCDF4")
    ncOUT.createDimension('longitude', jpi-cut)
    ncOUT.createDimension('latitude' ,jpj)
    if (fgroup not in [ 'CO2F','EXCO']) : ncOUT.createDimension('depth'    ,jpk)
    ncOUT.createDimension('time'     ,  0)
    
    setattr(ncOUT,'Conventions'  ,'CF-1.4' )
    setattr(ncOUT,'reference'   , "https://marine.copernicus.eu/") # requirement BO-113
    setattr(ncOUT,'institution'  , inst    )
    setattr(ncOUT,'source'       , '3DVAR-OGSTM-BFM')
    setattr(ncOUT,'licence', 'http://marine.copernicus.eu/services-portfolio/service-commitments-and-licence/')
    setattr(ncOUT,'comment'      , ref)
    setattr(ncOUT,'contact'      ,'servicedesk.cmems@mercator-ocean.eu')
    setattr(ncOUT,'bulletin_date', bulletin_time.strftime("%Y-%m-%d") )
    setattr(ncOUT,'bulletin_type', bulletin_type)
    setattr(ncOUT,'history', "Output of MEDBFM4.4 model, post-processed by OGS, Sgonico (Trieste) - Italy, " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") )

    
    basename = os.path.basename(filename)
    if args.tr=='daily'   : timestr = basename[:8] + "-12:00:00"
    if args.tr=='monthly' : timestr = basename[:6] + "01-00:00:00" # 01 of every month
    D = datetime.datetime.strptime(timestr,'%Y%m%d-%H:%M:%S')
    Dref = datetime.datetime(1970,1,1,0,0,0)
    Diff = D-Dref
    if DType in ["sm", "fc"]:
        Diff_forecast = bulletin_time - Dref
    
    ncvar = ncOUT.createVariable('time','d',('time',))
    setattr(ncvar,'units',       'seconds since 1970-01-01 00:00:00')
    setattr(ncvar,'long_name'    ,'time')
    setattr(ncvar,'standard_name','time')
    setattr(ncvar,'axis'         ,'T')
    setattr(ncvar,'calendar'     ,'standard')
    ncvar[:] = Diff.days*3600*24 + Diff.seconds
    
    if (fgroup not in [ 'CO2F', 'EXCO'] ) :
        ncvar = ncOUT.createVariable('depth'   ,'f', ('depth',))
        setattr(ncvar,'units'        ,'m')
        setattr(ncvar,'long_name'    ,'depth')
        setattr(ncvar,'standard_name','depth')
        setattr(ncvar,'positive'     ,'down')
        setattr(ncvar,'axis'         ,'Z')
        ncvar[:] = nav_lev
    
    ncvar = ncOUT.createVariable('latitude','f' ,('latitude',))
    setattr(ncvar, 'units'        ,'degrees_north')
    setattr(ncvar,'long_name'    ,'latitude')
    setattr(ncvar,'standard_name','latitude')
    setattr(ncvar, 'axis'         ,'Y')
    ncvar[:]=Lat

    ncvar = ncOUT.createVariable('longitude','f',('longitude',))
    setattr(ncvar, 'units'        ,'degrees_east')
    setattr(ncvar,'long_name'    ,'longitude')
    setattr(ncvar, 'standard_name','longitude')
    setattr(ncvar, 'axis'         ,'X')
    ncvar[:]=Lon

    if DType in ["sm", "fc"]:
        ncvar = ncOUT.createVariable('Forecast_Reference_Time','d',('time',)) # requirement BO-115
        ncvar[:] = Diff_forecast.days*3600*24 + Diff_forecast.seconds
        setattr(ncvar, 'units', 'seconds since 1970-01-01 00:00:00')
        setattr(ncvar, 'standard_name', 'forecast_reference_time')
        setattr(ncvar, 'long_name', 'Reference time that initiates the forecast')
        setattr(ncvar, 'calendar', 'standard')
        setattr(ncvar, 'comment', 'For analysis products, the value is the same as the time variable, for forecast products, the value is the time of the first forecast step')

    ncvar = ncOUT.createVariable('Processing_Status','i','time') # requirement BO-116
    ncvar[:] = StatusFlag
    setattr(ncvar, 'standard_name','status_flag')
    setattr(ncvar, 'long_name'   ,'Data processing status flag')
    setattr(ncvar, 'flag_values' , [0,1])
    setattr(ncvar, 'flag_meanings', 'consolidated intermediate')
    setattr(ncvar, 'comment'  ,'Value of 0 means that the field is consolidated, value of 1 means that the field is intermediate and will be updated in the next bulletin')
    
    
    return ncOUT


def set_filename(timeobj,FGroup):
    return timeobj.strftime('%Y%m%d_') + tr + "-OGS--" + FGroup + "-MedBFM4.4-MED-b" + bulletin_date +"_" + DType + "-sv13.00.nc"

for timestr in TIMELIST[rank::nranks]:
    timeobj = datetime.datetime.strptime(timestr,"%Y%m%d")
    for FGroup in FGROUPS:
        product_file = set_filename(timeobj, FGroup)
        print("rank =", rank, product_file, flush=True)
        ncOUT = create_Structure(OUTPUTDIR + product_file,FGroup)
        
        
        if FGroup == 'NUTR':
            if args.tr=='daily'  : setattr(ncOUT,'title','Nitrate, Phosphate, Ammonium and Silicate (3D) - Daily Mean')
            if args.tr=='monthly': setattr(ncOUT,'title','Nitrate, Phosphate, Ammonium and Silicate (3D) - Monthly Mean')
            
            ncvar = ncOUT.createVariable('no3', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Nitrate')
            setattr(ncvar,'standard_name','mole_concentration_of_nitrate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "N3n")
            ncvar[0,:] = M
            
            
            ncvar = ncOUT.createVariable('po4', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Phosphate')
            setattr(ncvar,'standard_name','mole_concentration_of_phosphate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            
            M = readdata(timestr, "N1p")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('nh4', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Ammonium')
            setattr(ncvar,'standard_name','mole_concentration_of_ammonium_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')

            M = readdata(timestr, "N4n")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('si', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Silicate')
            setattr(ncvar,'standard_name','mole_concentration_of_silicate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')

            M = readdata(timestr, "N5s")
            ncvar[0,:] = M

        if FGroup == 'PFTC':
            if args.tr=='daily'   : setattr(ncOUT,'title','Phytoplankton Carbon Biomass, Zooplankton Carbon Biomass, Chlorophyll and PFTs (3D) - Daily Mean')
            if args.tr=='monthly' : setattr(ncOUT,'title','Phytoplankton Carbon Biomass, Zooplankton Carbon Biomass, Chlorophyll and PFTs (3D) - Monthly Mean')

            ncvar = ncOUT.createVariable('phyc', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Phytoplankton Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_phytoplankton_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            try:
                pcb = readdata(timestr, 'P_c') * (1./12.)
            except:
                print("using native P1c, P2c, P3c, P4c")
                P1c = readdata(timestr, "P1c")
                P2c = readdata(timestr, "P2c")
                P3c = readdata(timestr, "P3c")
                P4c = readdata(timestr, "P4c")
                pcb = (P1c + P2c + P3c +P4c)*(1./12.)
                #CONVERSION from "mgC m-3" to "mmolC m-3"
                # conversion factor: 1/12
            pcb[~tmask] = 1.e+20
            ncvar[0,:] = pcb
            
            ncvar = ncOUT.createVariable('diatoC', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Diatoms Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_diatoms_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P1c")* (1./12.)
            M[~tmask] = 1.e+20
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('nanoC', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Nanophytoplankton Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_nanophytoplankton_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P2c")* (1./12.)
            M[~tmask] = 1.e+20
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('picoC', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Picophytoplankton Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_picophytoplankton_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P3c")* (1./12.)
            M[~tmask] = 1.e+20
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('dinoC', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Dinoflagellates Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_dinoflagellates_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P4c")* (1./12.)
            M[~tmask] = 1.e+20
            ncvar[0,:] = M




            ncvar = ncOUT.createVariable('chl', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Chlorophyll')
            setattr(ncvar,'standard_name','mass_concentration_of_chlorophyll_a_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            try:
                chl = readdata(timestr, "P_l")
            except:
                print("using native P1l, P2l, P3l, P4l")
                P1l = readdata(timestr, "P1l")
                P2l = readdata(timestr, "P2l")
                P3l = readdata(timestr, "P3l")
                P4l = readdata(timestr, "P4l")
                chl = (P1l + P2l + P3l +P4l)
            chl[~tmask] = 1.e+20
            ncvar[0,:] = chl

            ncvar = ncOUT.createVariable('diatoChla', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Diatoms Chlorophyll concentration')
            setattr(ncvar,'standard_name','mass_concentration_of_diatoms_expressed_as_chlorophyll_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P1l")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('nanoChla', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Nanophytoplankton Chlorophyll concentration')
            setattr(ncvar,'standard_name','mass_concentration_of_nanophytoplankton_expressed_as_chlorophyll_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P2l")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('picoChla', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Picophytoplankton Chlorophyll concentration')
            setattr(ncvar,'standard_name','mass_concentration_of_picophytoplankton_expressed_as_chlorophyll_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P3l")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('dinoChla', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Dinoflagellates Chlorophyll concentration')
            setattr(ncvar,'standard_name','mass_concentration_of_dinoflagellates_expressed_as_chlorophyll_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "P4l")
            ncvar[0,:] = M



            ncvar = ncOUT.createVariable('zooc', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Zooplankton Carbon Biomass')
            setattr(ncvar,'standard_name','mole_concentration_of_zooplankton_expressed_as_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')

            try:
                Z_c = readdata(timestr, "Z_c")* (1./12.)
            except:
                print("using native Z3c, Z4c, Z5c, Z6c")
                Z3c = readdata(timestr, "Z3c")
                Z4c = readdata(timestr, "Z4c")
                Z5c = readdata(timestr, "Z5c")
                Z6c = readdata(timestr, "Z6c")
                Z_c = (Z3c + Z4c + Z5c +Z6c)* (1./12.)
            Z_c[~tmask] = 1.e+20
            ncvar[0,:] = Z_c


        if FGroup == 'BIOL':
            if args.tr=='daily'  : setattr(ncOUT, 'title', "Primary Production and Oxygen (3D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title', "Primary Production and Oxygen (3D) - Monthly Mean")
            
            ncvar = ncOUT.createVariable('o2', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Dissolved oxygen')
            setattr(ncvar,'standard_name','mole_concentration_of_dissolved_molecular_oxygen_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            O2o = readdata(timestr,"O2o")
            ncvar[0,:] = O2o
            
            ncvar = ncOUT.createVariable('nppv', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3 day-1')
            setattr(ncvar,'long_name'    ,'Net Primary Production')
            setattr(ncvar,'standard_name','net_primary_production_of_biomass_expressed_as_carbon_per_unit_volume_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ppn = readdata(timestr,"ppn")
            ncvar[0,:] = ppn
            
        if FGroup == 'CARB':
            if args.tr=='daily'  : setattr(ncOUT, 'title',"Dissolved Inorganic Carbon, pH and Alkalinity (3D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title',"Dissolved Inorganic Carbon, pH and Alkalinity (3D) - Monthly Mean")
            

            ncvar = ncOUT.createVariable('ph', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'1')
            setattr(ncvar,'long_name'    ,'Ocean pH')
            setattr(ncvar,'standard_name','sea_water_ph_reported_on_total_scale')
            setattr(ncvar,'comment'         , 'pH reported on total scale at in situ Temp and Press conditions')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ph = readdata(timestr, "pH")
            ncvar[0,:] =ph

            ncvar = ncOUT.createVariable('dissic', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3')
            setattr(ncvar,'long_name'    ,"Dissolved Inorganic Carbon")
            setattr(ncvar,'standard_name','mole_concentration_of_dissolved_inorganic_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            setattr(ncvar,'comment'         , 'In order to calculate DIC in [micro mol / kg of seawater], dissic has to be multiplied by (1.e+6 / seawater density [kg/m3])')
            dic = readdata(timestr, "O3c")/(12*1000) # conversion mg/mol
            dic[~tmask] = 1.e+20
            ncvar[0,:] =dic

            ncvar = ncOUT.createVariable('talk', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3')
            setattr(ncvar,'long_name'    ,"Alkalinity")
            setattr(ncvar,'standard_name','sea_water_alkalinity_expressed_as_mole_equivalent')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            setattr(ncvar,'comment'         , 'In order to calculate ALK in [micro mol / kg of seawater], talk has to be multiplied by (1.e+6 / seawater density [kg/m3])')
            alk = readdata(timestr, "O3h")/1000 # conversion mg/mol
            alk[~tmask] = 1.e+20
            ncvar[0,:] = alk


        if FGroup == 'CO2F':
            if args.tr=='daily'  : setattr(ncOUT, 'title',"Surface partial pressure of CO2 and Surface CO2 flux (2D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title',"Surface partial pressure of CO2 and Surface CO2 flux (2D) - Monthly Mean")
            ncvar = ncOUT.createVariable('fgco2', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'kg m-2 s-1')
            setattr(ncvar,'long_name'    ,"Surface CO2 flux")
            setattr(ncvar,'standard_name','surface_downward_mass_flux_of_carbon_dioxide_expressed_as_carbon')
            setattr(ncvar,'comment'    ,"surface downward flux at air-sea interface of carbon dioxide expressed as kg of carbon per square meter per second")
            setattr(ncvar,'coordinates'  ,'time latitude longitude')
            co2_airflux = readdata(timestr, "CO2airflux", ndims=2) *12 * 1.e-6 /86400 # conversion from mmol m-2 day-1 to kg/m2/s
            co2_airflux[~tmask[0,:,:]] = 1.e+20
            ncvar[0,:] =co2_airflux

            ncvar = ncOUT.createVariable('spco2', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'Pa')
            setattr(ncvar,'long_name'    ,'Surface partial pressure of CO2')
            setattr(ncvar,'standard_name','surface_partial_pressure_of_carbon_dioxide_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time latitude longitude')
            pco2 = readdata(timestr, "pCO2") *0.101325 #conversion microatm --> Pascal  1 ppm = 1 microatm = 1.e-6 * 101325 Pa
            pco2[~tmask] = 1.e+20
            ncvar[0,:] = pco2[0,:,:]

        if FGroup == 'EXCO':
            if args.tr=='daily'  : setattr(ncOUT, 'title',"Attenuation coefficient of downwelling radiative flux (2D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title',"Attenuation coefficient of downwelling radiative flux (2D) - Monthly Mean")
            ncvar = ncOUT.createVariable('kd490', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'m-1')
            setattr(ncvar,'long_name'    ,"Diffuse attenuation coefficient of the downwelling irradiance at 490 nm")
            setattr(ncvar,'standard_name','volume_attenuation_coefficient_of_downwelling_radiative_flux_in_sea_water_490')
            setattr(ncvar,'coordinates'  ,'time latitude longitude')
            kd_490 = readdata(timestr, "kd490")
            ncvar[0,:] =kd_490[0,:]
        ncOUT.close()
        
