import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
   Creates COPERNICUS products files from reanalysis.
   Product name = MEDSEA_MULTIYEAR_BGC_006_008
   Standard names are choose from
   http://cfconventions.org/Data/cf-standard-names/30/build/cf-standard-name-table.html.

   Files have been checked from http://puma.nerc.ac.uk/cgi-bin/cf-checker.pl.

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
    parser.add_argument(    '--tr',
                                type = str,
                                required = True,
                                choices = ["daily","monthly","yearly"])

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
if args.bulltype == 'analysis' :
    DType     = "re"
    source    = '3DVAR-OGSTM-BFM'
else:
    DType     = "in"
    source    = '3DVAR-OGSTM-BFMI'
bulletin_date = args.bulltime
maskfile = args.maskfile
if args.tr=='daily'  :
    tr='d'
    field_type='daily_mean_centered_at_time_field'
if args.tr=='monthly':
    tr='m'
    field_type='monthly_mean_beginning_at_time_field'
if args.tr=='yearly':
    tr='y'
    field_type='yearly_mean_beginning_at_time_field'


cut = 80 #1/24
TheMask = Mask.from_file(maskfile, ylevels_var_name="gphit", xlevels_var_name="glamt")
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

def readdata(time, var, ndims=3):
    
    inputfile = INPUTDIR + "ave."  + time + "-12:00:00." + var + ".nc"
    return readfile(inputfile,var,ndims=ndims)

def create_Structure(filename, fgroup):
    ref=  'Please check in CMEMS catalogue the INFO section for product MEDSEA_MULTIYEAR_BGC_006_008 - http://marine.copernicus.eu/'
    ref2 = "Teruzzi, A., Feudale, L., Bolzon, G., Lazzari, P., Salon, S., Di Biagio, V., Coidessa, G., & Cossarini, G. (2021). Mediterranean Sea Biogeochemical Reanalysis INTERIM (CMEMS MED-Biogeochemistry, MedBFM3i system) (Version 1) [Data set]. Copernicus Monitoring Environment Marine Service (CMEMS). https://doi.org/10.25423/CMCC/MEDSEA_MULTIYEAR_BGC_006_008_MEDBFM3I"
    inst  ='OGS (Istituto Nazionale di Oceanografia e di Geofisica Sperimentale) , Sgonico (Trieste) - Italy'
    ncOUT = netCDF4.Dataset(filename,"w",format="NETCDF4")
    ncOUT.createDimension('longitude', jpi-cut)
    ncOUT.createDimension('latitude' ,jpj)
    if (fgroup != 'CO2F') : ncOUT.createDimension('depth'    ,jpk)
    ncOUT.createDimension('time'     ,  0)
    
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
    
    basename = os.path.basename(filename)
    if args.tr=='daily'   : timestr = basename[:8] + "-12:00:00"
    if args.tr=='monthly' : timestr = basename[:6] + "01-00:00:00" # 01 of every month
    if args.tr=='yearly'  : timestr = basename[:4] + "0101-00:00:00" # 0101 of every year
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
    
    if (fgroup != 'CO2F') :
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


def V5_filename(timeobj,FGroup):
    if args.bulltype == 'analysis':
        return timeobj.strftime('%Y%m%d_') + tr + "-OGS--" + FGroup + "-MedBFM3-MED-b" + bulletin_date +"_" + DType + "-sv05.00.nc"
    else:
        return timeobj.strftime('%Y%m%d_') + tr + "-OGS--" + FGroup + "-MedBFM3i-MED-b" + bulletin_date +"_" + DType + "-sv05.00.nc"

for timestr in TIMELIST[rank::nranks]:
    timeobj = datetime.datetime.strptime(timestr,"%Y%m%d")
    for FGroup in FGROUPS:
        product_file = V5_filename(timeobj, FGroup)
        print("rank =", rank, product_file, flush=True)
        ncOUT = create_Structure(OUTPUTDIR + product_file,FGroup)
        
        
        if FGroup == 'NUTR':
            if args.tr=='daily'  : setattr(ncOUT,'title','Nitrate, Phosphate and Ammonium (3D) - Daily Mean')
            if args.tr=='monthly': setattr(ncOUT,'title','Nitrate, Phosphate and Ammonium (3D) - Monthly Mean')
            if args.tr=='yearly' : setattr(ncOUT,'title','Nitrate, Phosphate and Ammonium (3D) - Yearly Mean')
            
            ncvar = ncOUT.createVariable('no3', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Nitrate in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_nitrate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            M = readdata(timestr, "N3n")
            ncvar[0,:] = M
            
            
            ncvar = ncOUT.createVariable('po4', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Phosphate in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_phosphate_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            
            
            M = readdata(timestr, "N1p")
            ncvar[0,:] = M

            ncvar = ncOUT.createVariable('nh4', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Ammonium in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_ammonium_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')

            M = readdata(timestr, "N4n")
            ncvar[0,:] = M


        if FGroup == 'PFTC':
            if args.tr=='daily'   : setattr(ncOUT,'title','Phytoplankton Carbon Biomass and Chlorophyll (3D) - Daily Mean')
            if args.tr=='monthly' : setattr(ncOUT,'title','Phytoplankton Carbon Biomass and Chlorophyll (3D) - Monthly Mean')
            if args.tr=='yearly'  : setattr(ncOUT,'title','Phytoplankton Carbon Biomass and Chlorophyll (3D) - Yearly Mean')

            ncvar = ncOUT.createVariable('phyc', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Concentration of Phytoplankton Biomass in sea water')
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
            
            ncvar = ncOUT.createVariable('chl', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3')
            setattr(ncvar,'long_name'    ,'Concentration of Chlorophyll in sea water')
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



        if FGroup == 'BIOL':
            if args.tr=='daily'  : setattr(ncOUT, 'title', "Primary Production and Oxygen (3D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title', "Primary Production and Oxygen (3D) - Monthly Mean")
            if args.tr=='yearly' : setattr(ncOUT, 'title', "Primary Production and Oxygen (3D) - Yearly Mean")
            
            ncvar = ncOUT.createVariable('o2', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mmol m-3')
            setattr(ncvar,'long_name'    ,'Mole concentration of Dissolved Molecular Oxygen in sea water')
            setattr(ncvar,'standard_name','mole_concentration_of_dissolved_molecular_oxygen_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            O2o = readdata(timestr,"O2o")
            ncvar[0,:] = O2o
            
            ncvar = ncOUT.createVariable('nppv', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mg m-3 day-1')
            setattr(ncvar,'long_name'    ,'Net Primary Production in sea water')
            setattr(ncvar,'standard_name','net_primary_production_of_biomass_expressed_as_carbon_per_unit_volume_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ppn = readdata(timestr,"ppn")
            ncvar[0,:] = ppn
            
        if FGroup == 'CARB':
            if args.tr=='daily'  : setattr(ncOUT, 'title',"Dissolved Inorganic Carbon, pH and Alkalinity (3D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title',"Dissolved Inorganic Carbon, pH and Alkalinity (3D) - Monthly Mean")
            if args.tr=='yearly' : setattr(ncOUT, 'title',"Dissolved Inorganic Carbon, pH and Alkalinity (3D) - Yearly Mean")

            ncvar = ncOUT.createVariable('ph', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'1')
            setattr(ncvar,'long_name'    ,'PH')
            setattr(ncvar,'standard_name','sea_water_ph_reported_on_total_scale')
            setattr(ncvar,'info'         , 'pH reported on total scale at in situ Temp and Press conditions')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            ph = readdata(timestr, "pH")
            ncvar[0,:] =ph

            ncvar = ncOUT.createVariable('dissic', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3')
            setattr(ncvar,'long_name'    ,"Mole concentration of dissolved inorganic carbon in sea water")
            setattr(ncvar,'standard_name','mole_concentration_of_dissolved_inorganic_carbon_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            setattr(ncvar,'info'         , 'In order to calculate DIC in [micro mol / kg of seawater], dissic has to be multiplied by (1.e+6 / seawater density [kg/m3])')
            dic = readdata(timestr, "O3c")/(12*1000) # conversion mg/mol
            dic[~tmask] = 1.e+20
            ncvar[0,:] =dic

            ncvar = ncOUT.createVariable('talk', 'f', ('time','depth','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'mol m-3')
            setattr(ncvar,'long_name'    ,"Alkalinity")
            setattr(ncvar,'standard_name','sea_water_alkalinity_expressed_as_mole_equivalent')
            setattr(ncvar,'coordinates'  ,'time depth latitude longitude')
            setattr(ncvar,'info'         , 'In order to calculate ALK in [micro mol / kg of seawater], talk has to be multiplied by (1.e+6 / seawater density [kg/m3])')
            alk = readdata(timestr, "O3h")/1000 # conversion mg/mol
            alk[~tmask] = 1.e+20
            ncvar[0,:] = alk


        if FGroup == 'CO2F':
            if args.tr=='daily'  : setattr(ncOUT, 'title',"Surface partial pressure of CO2 and Surface CO2 flux (2D) - Daily Mean")
            if args.tr=='monthly': setattr(ncOUT, 'title',"Surface partial pressure of CO2 and Surface CO2 flux (2D) - Monthly Mean")
            if args.tr=='yearly' : setattr(ncOUT, 'title',"Surface partial pressure of CO2 and Surface CO2 flux (2D) - Yearly Mean")

            ncvar = ncOUT.createVariable('fpco2', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'kg m-2 s-1')
            setattr(ncvar,'long_name'    ,"surface downward flux at air-sea interface of carbon dioxide expressed as kg of carbon per square meter per second")
            setattr(ncvar,'standard_name','surface_downward_mass_flux_of_carbon_dioxide_expressed_as_carbon')
            setattr(ncvar,'coordinates'  ,'time latitude longitude')
            co2_airflux = readdata(timestr, "CO2airflux", ndims=2) *12 * 1.e-6 /86400 # conversion from mmol m-2 day-1 to kg/m2/s
            co2_airflux[~tmask[0,:,:]] = 1.e+20
            ncvar[0,:] =co2_airflux

            ncvar = ncOUT.createVariable('spco2', 'f', ('time','latitude','longitude'),zlib=True, fill_value=1.0e+20)
            setattr(ncvar,'missing_value',ncvar._FillValue)
            setattr(ncvar,'units'        ,'Pa')
            setattr(ncvar,'long_name'    ,'Surface partial pressure of carbon dioxide in sea water')
            setattr(ncvar,'standard_name','surface_partial_pressure_of_carbon_dioxide_in_sea_water')
            setattr(ncvar,'coordinates'  ,'time latitude longitude')
            pco2 = readdata(timestr, "pCO2") *0.101325 #conversion microatm --> Pascal  1 ppm = 1 microatm = 1.e-6 * 101325 Pa
            pco2[~tmask] = 1.e+20
            ncvar[0,:] = pco2[0,:,:]
        ncOUT.close()
        
