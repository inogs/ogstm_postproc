import argparse
def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates Float_Index.txt files.
    ''', formatter_class=argparse.RawTextHelpFormatter)


    parser.add_argument(   '--inputdir','-i',
                                type = str,
                                required = True,
                                default = "/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/POSTPROC/output/MONTHLY/AVE/",
                                help = 'directory with ave files')
    parser.add_argument(   '--outdir','-o',
                                type = str,
                                required = True,
                                default = "/gpfs/scratch/userexternal/gbolzon0/OPEN_BOUNDARY/TEST_05/wrkdir/POSTPROC/output/MONTHLY/INTEGRATED/",
                                help = 'path of the output dir')
    parser.add_argument(   '--maskfile','-m',
                                type = str,
                                required = True,
                                help = 'path of mask file')
    parser.add_argument(   '--var','-v',
                                type = str,
                                required = True,
                                help = 'var name')     

    return parser.parse_args()

args = argument()


from commons.dataextractor import DataExtractor
from commons.Timelist import TimeList,TimeInterval
from commons.mask import Mask
from commons.layer import Layer
from layer_integral.mapbuilder import MapBuilder
from commons.utils import addsep
import GB_lib
import numpy as np
import netCDF4

var=args.var

INPUTDIR=addsep(args.inputdir)
OUTDIR  =addsep(args.outdir)
TheMask= Mask(args.maskfile)
_,jpj,jpi = TheMask.shape

TI=TimeInterval("2017","2018","%Y")
TL=TimeList.fromfilenames(TI, INPUTDIR, "ave*nc", filtervar=var)
LAYERLIST=[Layer(0,50), Layer(50,100), Layer(100,150)]

nFrames = TL.nTimes
ndepth  = len(LAYERLIST)

def dump_integrated_file(outfile, M, varname, lon, lat):
    ncOUT = netCDF4.Dataset(outfile,'w')
    
    nFrames, jpk, jpj, jpi= M.shape
    ncOUT.createDimension("longitude", jpi)
    ncOUT.createDimension("latitude", jpj)
    ncOUT.createDimension("layers"  , jpk)
    ncOUT.createDimension("nFrames" , nFrames)
    ncvar = ncOUT.createVariable('longitude', 'f', ('longitude',))
    ncvar[:] = lon
    ncvar = ncOUT.createVariable('latitude', 'f', ('latitude',))
    ncvar[:] = lat
    ncvar = ncOUT.createVariable(varname, 'f', ('nFrames', 'layers','latitude','longitude'))
    setattr(ncvar,'fillValue'    ,1.e+20)
    setattr(ncvar,'missing_value',1.e+20)

    ncvar[:] = M
    ncOUT.close() 

M = np.zeros((nFrames,ndepth,jpj,jpi),np.float32)
longitude=TheMask.xlevels[0, :]
latitude =TheMask.ylevels[:, 0]


for iFrame, filename in enumerate(TL.filelist):
    F=GB_lib.filename_manager(filename)
    De=DataExtractor(TheMask,filename,var)
    for ilayer, layer in enumerate(LAYERLIST):
        #outfile= "%s%s.%s.%s.%s.nc" %( OUTDIR, F.prefix, F.datestr, F.varname, layer.string())
        #print outfile
        mask=TheMask.mask_at_level(layer.top)
        integrated = MapBuilder.get_layer_integral(De, layer)
        integrated[~mask] = 1.e+20
        M[iFrame,ilayer,:,:] = integrated
        #netcdf3.write_2d_file(integrated,var,outfile,TheMask)
outfile=OUTDIR + var + ".nc"
dump_integrated_file(outfile, M, var, longitude, latitude)