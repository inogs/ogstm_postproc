import argparse
# def argument():
    # parser = argparse.ArgumentParser(description = '''
    # Generates climatological 3d files.
    # Origin files are Re-analysis 3d monthly files, 
    #
    # output files
    # are on product mesh, cutted at Gib.
    # ''',
    # formatter_class=argparse.ArgumentDefaultsHelpFormatter
    # )
    # parser.add_argument(   '--inputdir', '-i',
                                # type = str,
                                # required = True,
                                # help = ''' '''
                                #
                                # )
                                #
    # parser.add_argument(   '--maskfile', '-m',
                                # type = str,
                                # required = True,
                                # help = ''' mask filename .'''
                                # )
                                #
    # parser.add_argument(   '--outdir', '-o',
                                # type = str,
                                # required = True,
                                # help = ''' output directory'''
                                # )
    # parser.add_argument(   '--var', '-v',
                                # type = str,
                                # required = True,
                                # help = ''' model var name'''
                                # )
    # return parser.parse_args()
    #
    #
# args = argument()


from bitsea.commons.Timelist import TimeInterval,TimeList
from bitsea.commons import timerequestors
from bitsea.commons.time_averagers import TimeAverager3D
from bitsea.commons.mask import Mask
from bitsea.commons import netcdf4
from bitsea.commons import interpolators
from bitsea.commons.utils import file2stringlist


try:
    from mpi4py import MPI
    comm  = MPI.COMM_WORLD
    rank  = comm.Get_rank()
    nranks =comm.size
except:
    rank   = 0
    nranks = 1



MaskRA_24    = Mask('/g100_scratch/userexternal/gbolzon0/RA_24/meshmask.nc')
Mask__NRT    = Mask('/g100_scratch/userexternal/gbolzon0/RA_24/meshmask_NRT.nc')
Mask_006_014 = Mask('/g100_scratch/userexternal/gbolzon0/RA_24/meshmask_006_014.nc')
    
cut = 80

# grep ctrcnm /gpfs/work/IscrC_REBIOMED/REANALISI_24/ModelBuild/ogstm/ready_for_model_namelists/namelist.passivetrc | cut -d "\"" -f 2

INPUTDIR="/g100_scratch/userexternal/gbolzon0/RA_24/CLIMATOLOGIES/MONTHLY/"
OUTDIR = "/g100_scratch/userexternal/gbolzon0/RA_24/CLIMATOLOGIES/output/MONTHLY/"

VARLIST=file2stringlist("state_vars.txt")
for var in VARLIST[rank::nranks]:
    TL=TimeList.fromfilenames(None, INPUTDIR, "ave*.nc" , filtervar=var)

    for m in range(1,13):
        req= timerequestors.Clim_month(m)
        ii,w = TL.select(req)
        filelist=[TL.filelist[k] for k in ii] 
        M3d=TimeAverager3D(filelist, w, var, MaskRA_24)# 20s
        M_on_NRT=interpolators.interp_same_resolution(MaskRA_24, Mask__NRT, M3d)
        M_on_NRT[~Mask__NRT.mask]=1.e+20
        outfile= OUTDIR + "clim_monthly_%s_%02d.nc" %(var,m)
        print(outfile)
        netcdf4.write_3d_file(M_on_NRT[:,:,cut:], var, outfile, Mask_006_014, compression=True, thredds=True)
        
OUTDIR = "/g100_scratch/userexternal/gbolzon0/RA_24/CLIMATOLOGIES/output/ANNUAL/"
TI = TimeInterval("1999","2020","%Y")
for var in VARLIST[rank::nranks]:
    TL=TimeList.fromfilenames(None, INPUTDIR, "ave*.nc" , filtervar=var)
    ii,w=TL.select(timerequestors.Generic_req(TI)) 
    filelist=[TL.filelist[k] for k in ii] 
    M3d=TimeAverager3D(filelist, w, var, MaskRA_24)
    M_on_NRT=interpolators.interp_same_resolution(MaskRA_24, Mask__NRT, M3d)
    M_on_NRT[~Mask__NRT.mask]=1.e+20
    outfile= OUTDIR + "clim_annually_%s.nc" %(var)
    print(outfile)
    netcdf4.write_3d_file(M_on_NRT[:,:,cut:], var, outfile, Mask_006_014, compression=True, thredds=True)   
        

