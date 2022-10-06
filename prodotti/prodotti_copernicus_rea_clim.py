import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
   Creates COPERNICUS products files from reanalysis.
   Product name = MEDSEA_MULTIYEAR_BGC_006_008
   Standard names are choose from
   http://cfconventions.org/Data/cf-standard-names/30/build/cf-standard-name-table.html.

   Files have been checked from http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl.

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

    parser.add_argument(    '--bulltime',"-b",
                                type = str,
                                required = True,
                                help = '''The bulletin time a string time in the format yyyymmdd ''')
    parser.add_argument(    '--bulltype',
                                type = str,
                                required = True,
                                choices = ["analysis","interim"])# it should be reanalysis
    parser.add_argument(    '--maskfile', "-m",
                                type = str,
                                required = True,
                                help = '''Path for the maskfile ''')


    return parser.parse_args()


args = argument()

import netCDF4
import numpy as np
import datetime,os
from commons.utils import addsep
from commons.mask import Mask
from commons.dataextractor_open import DataExtractor

INPUTDIR  = addsep(args.inputdir)
OUTPUTDIR = addsep(args.outputdir)

if args.bulltype == 'analysis' :
    DType     = "re"
    source    = '3DVAR-OGSTM-BFM'
else:
    DType     = "in"
    source    = '3DVAR-OGSTM-BFMI'
bulletin_date = args.bulltime
maskfile = args.maskfile


tr='m'
field_type='monthly_climatology'

    

cut = 80 #1/24
TheMask = Mask(maskfile,ylevelsmatvar="gphit", xlevelsmatvar="glamt")
jpk, jpj, jpi = TheMask.shape
nav_lev = TheMask.zlevels
Lon = TheMask.xlevels[0,:].astype(np.float32)
Lat = TheMask.ylevels[:,0].astype(np.float32)
tmask = TheMask.mask

Lon = Lon[cut:]
tmask = tmask[:,:,cut:]

FGROUPS = ['NUTR', 'PFTC', 'BIOL', 'CARB','CO2F']

bulletin_type='analysis'


bulletin_time = datetime.datetime.strptime(bulletin_date,"%Y%m%d")

def readfile(filename,var,ndims):
    M=DataExtractor(TheMask,filename,var, dimvar=ndims).values
    if ndims==3:return M[:,:,cut:]
    if ndims==2:return M[:,cut:]

def readdata(time, var, ndims=3, std=False ):
    
    inputfile = INPUTDIR + "ave."  + time + "-00:00:00." + var + ".nc"
    print(inputfile)
    if std:
        return readfile(inputfile,var + "_std", ndims=ndims)
    else:
        return readfile(inputfile,var,ndims=ndims)

def create_Structure(filename):
    ref=  'Please check in CMEMS catalogue the INFO section for product MEDSEA_MULTIYEAR_BGC_006_008 - http://marine.copernicus.eu/'
    ref2 = "Teruzzi, A., Feudale, L., Bolzon, G., Lazzari, P., Salon, S., Di Biagio, V., Coidessa, G., & Cossarini, G. (2021). Mediterranean Sea Biogeochemical Reanalysis INTERIM (CMEMS MED-Biogeochemistry, MedBFM3i system) (Version 1) [Data set]. Copernicus Monitoring Environment Marine Service (CMEMS). https://doi.org/10.25423/CMCC/MEDSEA_MULTIYEAR_BGC_006_008_MEDBFM3I"
    inst  ='OGS (Istituto Nazionale di Oceanografia e di Geofisica Sperimentale) , Sgonico (Trieste) - Italy'
    ncOUT = netCDF4.Dataset(filename,"w",format="NETCDF4")
    ncOUT.createDimension('longitude', jpi-cut)
    ncOUT.createDimension('latitude' ,jpj)
    ncOUT.createDimension('depth'    ,jpk)
    ncOUT.createDimension('time'     , 12)
    
    setattr(ncOUT,'Conventions'  ,'CF-1.0' )
    if args.bulltype == 'analysis':
        setattr(ncOUT,'references'   , ref    )
    else:
        setattr(ncOUT,'references'   , ref2    )
    setattr(ncOUT,'institution'  , inst    )
    setattr(ncOUT,'source'       , source)
    setattr(ncOUT,'comment'      , ref)
    setattr(ncOUT,'contact'      ,'servicedesk.cmems@mercator-ocean.eu')
    setattr(ncOUT,'bulletin_date', bulletin_time.strftime("%Y-%m-%d") )
    setattr(ncOUT,'bulletin_type', args.bulltype)
    setattr(ncOUT,'field_type'   , field_type)
    
    ncvar = ncOUT.createVariable('time','d',('time',))
    setattr(ncvar,'units',       'months')
    setattr(ncvar,'long_name'    ,'time')
    setattr(ncvar,'standard_name','time')
    setattr(ncvar,'axis'         ,'T')
    setattr(ncvar,'calendar'     ,'standard')
    ncvar[:] = np.arange(1,13)
    

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


product_file = "19990101-20191231_m-OGS--CLIM-MedBFM3-MED-b%s_re-sv05.00.nc" %(args.bulltime)
ncOUT = create_Structure(OUTPUTDIR + product_file)
setattr(ncOUT,'title','Monthly climatology reference period 1999-2019')
for FGroup in FGROUPS:

    if FGroup == 'NUTR':
        ncvar = ncOUT.createVariable('no3_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Nitrate')
        setattr(ncvar,'standard_name','mole_concentration_of_nitrate_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N3n")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('no3_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Nitrate standard deviation')
        setattr(ncvar,'standard_name','mole_concentration_of_nitrate_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N3n", std=True)
            ncvar[iFrame,:] = M
        

        ncvar = ncOUT.createVariable('po4_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Phosphate')
        setattr(ncvar,'standard_name','mole_concentration_of_phosphate_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N1p")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('po4_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Phosphate standard deviation')
        setattr(ncvar,'standard_name','mole_concentration_of_phosphate_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N1p", std=True)
            ncvar[iFrame,:] = M


        ncvar = ncOUT.createVariable('nh4_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Ammonium')
        setattr(ncvar,'standard_name','mole_concentration_of_ammonium_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N4n")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('nh4_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Ammonium standard deviation')
        setattr(ncvar,'standard_name','mole_concentration_of_ammonium_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "N4n", std=True)
            ncvar[iFrame,:] = M




    if FGroup == 'PFTC':

        ncvar = ncOUT.createVariable('phyc_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Phytoplankton Carbon Biomass')
        setattr(ncvar,'standard_name','mole_concentration_of_phytoplankton_expressed_as_carbon_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
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
            ncvar[iFrame,:] = pcb

        ncvar = ncOUT.createVariable('phyc_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Phytoplankton Carbon Biomass standard deviation')
        setattr(ncvar,'standard_name','mole_concentration_of_phytoplankton_expressed_as_carbon_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            pcb = readdata(timestr, 'P_c', std=True) * (1./12.)
                #CONVERSION from "mgC m-3" to "mmolC m-3"
                # conversion factor: 1/12
            pcb[~tmask] = 1.e+20
            ncvar[iFrame,:] = pcb


        ncvar = ncOUT.createVariable('chl_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mg m-3')
        setattr(ncvar,'long_name'    ,'Chlorophyll')
        setattr(ncvar,'standard_name','mass_concentration_of_chlorophyll_a_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
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
            ncvar[iFrame,:] = chl

        ncvar = ncOUT.createVariable('chl_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mg m-3')
        setattr(ncvar,'long_name'    ,'Chlorophyll standard deviation')
        setattr(ncvar,'standard_name','mass_concentration_of_chlorophyll_a_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')

        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            chl = readdata(timestr, "P_l", std=True)
            chl[~tmask] = 1.e+20
            ncvar[iFrame,:] = chl


    if FGroup == 'BIOL':
        
        ncvar = ncOUT.createVariable('o2_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Dissolved oxygen')
        setattr(ncvar,'standard_name','mole_concentration_of_dissolved_molecular_oxygen_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "O2o")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('o2_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mmol m-3')
        setattr(ncvar,'long_name'    ,'Dissolved oxygen standard deviation')
        setattr(ncvar,'standard_name','mole_concentration_of_dissolved_molecular_oxygen_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "O2o", std=True)
            ncvar[iFrame,:] = M

        
        ncvar = ncOUT.createVariable('nppv_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mg m-3 day-1')
        setattr(ncvar,'long_name'    ,'Net Primary Production')
        setattr(ncvar,'standard_name','net_primary_production_of_biomass_expressed_as_carbon_per_unit_volume_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "ppn")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('nppv_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mg m-3 day-1')
        setattr(ncvar,'long_name'    ,'Net Primary Production standard deviation')
        setattr(ncvar,'standard_name','net_primary_production_of_biomass_expressed_as_carbon_per_unit_volume_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "ppn", std=True)
            ncvar[iFrame,:] = M

        
    if FGroup == 'CARB':

        ncvar = ncOUT.createVariable('ph_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'1')
        setattr(ncvar,'long_name'    ,'Ocean pH')
        setattr(ncvar,'standard_name','sea_water_ph_reported_on_total_scale')
        setattr(ncvar,'info'         , 'pH reported on total scale at in situ Temp and Press conditions')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "pH")
            ncvar[iFrame,:] = M

        ncvar = ncOUT.createVariable('ph_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'1')
        setattr(ncvar,'long_name'    ,'Ocean pH standard deviation')
        setattr(ncvar,'standard_name','sea_water_ph_reported_on_total_scale')
        setattr(ncvar,'info'         , 'pH reported on total scale at in situ Temp and Press conditions')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            M = readdata(timestr, "pH", std=True)
            ncvar[iFrame,:] = M          


        ncvar = ncOUT.createVariable('dissic_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mol m-3')
        setattr(ncvar,'long_name'    ,"Dissolved Inorganic Carbon")
        setattr(ncvar,'standard_name','mole_concentration_of_dissolved_inorganic_carbon_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        setattr(ncvar,'info'         , 'In order to calculate DIC in [micro mol / kg of seawater], dissic has to be multiplied by (1.e+6 / seawater density [kg/m3])')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            dic = readdata(timestr, "O3c")/(12*1000) # conversion mg/mol
            dic[~tmask] = 1.e+20
            ncvar[iFrame,:] = dic

        ncvar = ncOUT.createVariable('dissic_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mol m-3')
        setattr(ncvar,'long_name'    ,"Dissolved Inorganic Carbon standard deviation")
        setattr(ncvar,'standard_name','mole_concentration_of_dissolved_inorganic_carbon_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        setattr(ncvar,'info'         , 'In order to calculate DIC in [micro mol / kg of seawater], dissic has to be multiplied by (1.e+6 / seawater density [kg/m3])')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            dic = readdata(timestr, "O3c", std=True)/(12*1000) # conversion mg/mol
            dic[~tmask] = 1.e+20
            ncvar[iFrame,:] = dic


        ncvar = ncOUT.createVariable('talk_avg', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mol m-3')
        setattr(ncvar,'long_name'    ,"Alkalinity")
        setattr(ncvar,'standard_name','sea_water_alkalinity_expressed_as_mole_equivalent')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        setattr(ncvar,'info'         , 'In order to calculate ALK in [micro mol / kg of seawater], talk has to be multiplied by (1.e+6 / seawater density [kg/m3])')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            alk = readdata(timestr, "O3h")/1000 # conversion mg/mol
            alk[~tmask] = 1.e+20
            ncvar[iFrame,:] = alk

        ncvar = ncOUT.createVariable('talk_std', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'mol m-3')
        setattr(ncvar,'long_name'    ,"Alkalinity standard deviation")
        setattr(ncvar,'standard_name','sea_water_alkalinity_expressed_as_mole_equivalent')
        setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
        setattr(ncvar,'info'         , 'In order to calculate ALK in [micro mol / kg of seawater], talk has to be multiplied by (1.e+6 / seawater density [kg/m3])')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            alk = readdata(timestr, "O3h", std=True)/1000 # conversion mg/mol
            alk[~tmask] = 1.e+20
            ncvar[iFrame,:] = alk



    if FGroup == 'CO2F':      
        
        ncvar = ncOUT.createVariable('fgco2_avg', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'kg m-2 s-1')
        setattr(ncvar,'long_name'    ,"Surface CO2 flux")
        setattr(ncvar,'standard_name','surface_downward_mass_flux_of_carbon_dioxide_expressed_as_carbon')
        setattr(ncvar,'coordinates'  ,'time latitude longitude')
        setattr(ncvar,'info'         ,'surface downward flux at air-sea interface of carbon dioxide expressed as kg of carbon per square meter per second' )
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            co2_airflux = readdata(timestr, "CO2airflux", ndims=2) *12 * 1.e-6 /86400 # conversion from mmol m-2 day-1 to kg/m2/s
            co2_airflux[~tmask[0,:,:]] = 1.e+20
            ncvar[iFrame,:] =co2_airflux

        ncvar = ncOUT.createVariable('fgco2_std', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'kg m-2 s-1')
        setattr(ncvar,'long_name'    ,"Surface CO2 flux standard deviation")
        setattr(ncvar,'standard_name','surface_downward_mass_flux_of_carbon_dioxide_expressed_as_carbon')
        setattr(ncvar,'coordinates'  ,'time latitude longitude')
        setattr(ncvar,'info'         ,'surface downward flux at air-sea interface of carbon dioxide expressed as kg of carbon per square meter per second' )
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            co2_airflux = readdata(timestr, "CO2airflux", ndims=2, std=True) *12 * 1.e-6 /86400 # conversion from mmol m-2 day-1 to kg/m2/s
            co2_airflux[~tmask[0,:,:]] = 1.e+20
            ncvar[iFrame,:] =co2_airflux



        ncvar = ncOUT.createVariable('spco2_avg', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'Pa')
        setattr(ncvar,'long_name'    ,'Surface partial pressure of CO2')
        setattr(ncvar,'standard_name','surface_partial_pressure_of_carbon_dioxide_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            pco2 = readdata(timestr, "pCO2") *0.101325 #conversion microatm --> Pascal  1 ppm = 1 microatm = 1.e-6 * 101325 Pa
            pco2[~tmask] = 1.e+20
            ncvar[iFrame,:] = pco2[0,:,:]

        ncvar = ncOUT.createVariable('spco2_std', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
        setattr(ncvar,'missing_value',ncvar._FillValue)
        setattr(ncvar,'units'        ,'Pa')
        setattr(ncvar,'long_name'    ,'Surface partial pressure of CO2 standard deviation')
        setattr(ncvar,'standard_name','surface_partial_pressure_of_carbon_dioxide_in_sea_water')
        setattr(ncvar,'coordinates'  ,'time latitude longitude')
        for iFrame in range(12):
            timestr = "2000%02d01" %(iFrame+1)
            pco2 = readdata(timestr, "pCO2", std=True) *0.101325 #conversion microatm --> Pascal  1 ppm = 1 microatm = 1.e-6 * 101325 Pa
            pco2[~tmask] = 1.e+20
            ncvar[iFrame,:] = pco2[0,:,:]

ncOUT.close()
        
