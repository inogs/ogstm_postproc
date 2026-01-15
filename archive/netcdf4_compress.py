import argparse
import logging
from pathlib import Path

from bitsea.commons.netcdf4 import depth_dimension_name
from bitsea.commons.netcdf4 import lat_dimension_name
from bitsea.commons.netcdf4 import lon_dimension_name
from bitsea.utilities.argparse_types import existing_dir_path
from bitsea.utilities.mpi_serial_interface import get_mpi_communicator
import netCDF4
import numpy as np
from typing import Optional



if __name__ == '__main__':
    LOGGER = logging.getLogger()
else:
    LOGGER = logging.getLogger(__name__)


def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates netCDF4 compressed files

    Parallel executable can be called by mpirun.
   ''',formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(   '--inputdir', '-i',
                                type = existing_dir_path,
                                required = True,
                                help ='The directory wrkdir/MODEL/AVE_FREQ_1/ where chain has run.'
                                )
    parser.add_argument(   '--outputdir',"-o",
                                type = existing_dir_path,
                                required = True,
                                help = 'Path of existing dir')
    parser.add_argument(   '--filelist',"-l",
                                type = str,
                                default = "*.nc",
                                help = 'ave*.N1p.nc')
    parser.add_argument(   '--cutlevel',"-c",
                                required= False, 
                                type = int,
                                default = None,
                                help = 'depth levels on output files')  
 
    return parser.parse_args()

def WRITE_AVE(inputfile, outfile, var, var_args: Optional[dict] = None):
    if var_args is None:
        var_args = {}

    with netCDF4.Dataset(inputfile, "r") as ncIN:
        with netCDF4.Dataset(outfile, "w", format="NETCDF4") as ncOUT:
            setattr(ncOUT,"Convenctions", "COARDS")
            if "DateStart" in ncIN.ncattrs():
                setattr(ncOUT, "DateStart", ncIN.DateStart)
                setattr(ncOUT, "Date__End", ncIN.Date__End)

            DIMS=ncIN.dimensions
            for dimName,dimObj in DIMS.items():
                ncOUT.createDimension(dimName,dimObj.size)
            lon_orig_name=lon_dimension_name(ncIN)
            lat_orig_name=lat_dimension_name(ncIN)
            depth_orig_name=depth_dimension_name(ncIN)

            if 'depth' in ncIN.variables:
                ncvar = ncOUT.createVariable('depth'   ,'f', ('depth',))
                setattr(ncvar,'units','meter')
                setattr(ncvar,'positive','down')
                ncvar[:] = np.asarray(ncIN[depth_orig_name])

            ncvar = ncOUT.createVariable(lon_orig_name   ,'f',   (lon_orig_name,))
            setattr(ncvar,'units','degrees_east')
            setattr(ncvar,'long_name','Longitude')
            ncvar[:] = np.asarray(ncIN[lon_orig_name])

            ncvar = ncOUT.createVariable(lat_orig_name   ,'f',   (lat_orig_name,))
            setattr(ncvar,'units','degrees_north')
            setattr(ncvar,'long_name','Latitude')
            ncvar[:] = np.asarray(ncIN[lat_orig_name])

            OUT = np.asarray(ncIN[var][:])
            if 'time' in ncIN.dimensions:
                if len(OUT.shape)==4:
                    ncvar = ncOUT.createVariable(var, 'f', ('time','depth',lat_orig_name,lon_orig_name), **var_args)
                    setattr(ncvar,'missing_value', ncvar._FillValue)
                    setattr(ncvar,'long_name',var)
                    ncvar[:] = OUT
                if len(OUT.shape)==3:
                    ncvar = ncOUT.createVariable(var, 'f', ('time',lat_orig_name,lon_orig_name), **var_args)
                    setattr(ncvar,'missing_value', ncvar._FillValue)
                    setattr(ncvar,'long_name',var)
                    ncvar[:] =  OUT
            else:
                ncOUT.createDimension('time',0)
                if len(OUT.shape)==3:
                    ncvar = ncOUT.createVariable(var, 'f', ('time','depth',lat_orig_name,lon_orig_name), **var_args)
                    setattr(ncvar,'missing_value',ncvar._FillValue)
                    setattr(ncvar,'long_name',var)
                    ncvar[0,:] = OUT
                if len(OUT.shape)==2:
                    ncvar = ncOUT.createVariable(var, 'f', ('time',lat_orig_name,lon_orig_name), **var_args)
                    setattr(ncvar,'missing_value',ncvar._FillValue)
                    setattr(ncvar,'long_name',var)
                    ncvar[0,:] =  OUT

def WRITE_RST_DA(inputfile, outfile, var, jkcut: Optional[int] = None, var_args: Optional[dict] = None):
    if var_args is None:
        var_args = {}
    
    with netCDF4.Dataset(inputfile,"r") as ncIN:
        with netCDF4.Dataset(outfile,"w",format="NETCDF4") as ncOUT:
            in_dims = ncIN.dimensions
            for dim_name, dim_obj in in_dims.items():
                if jkcut is not None and dim_name in ["z","depth"]:
                    ncOUT.createDimension(dim_name, jkcut)
                else:
                    ncOUT.createDimension(dim_name, dim_obj.size)

            if 'time' not in in_dims.keys():
                ncOUT.createDimension('time',1)

            dims = (
                'time',
                depth_dimension_name(ncIN),
                lat_dimension_name(ncIN),
                lon_dimension_name(ncIN)
            )
            ncvar = ncOUT.createVariable("TRN" + var, 'f', dims , **var_args)
            setattr(ncvar,'missing_value', ncvar._FillValue)
            if var in ncIN.variables:
                x=np.asarray(ncIN[var][:])
            else:
                x=np.asarray(ncIN["TRN" + var][:])

            if len(x.shape)==4:
                ncvar[:] = x[:,:jkcut,:,:]
            else:
                ncvar[0,:] = x[:jkcut,:,:]

def WRITE_RST(inputfile, outfile, var, output_dtype=np.float64, var_args: Optional[dict] = None):
    """
    Valid for true restarts (51 variables, double)
    """

    with netCDF4.Dataset(inputfile,"r") as ncIN:
        with netCDF4.Dataset(outfile,"w",format="NETCDF4") as ncOUT:
            input_dims = ncIN.dimensions
            for dim_name, dim_obj in input_dims.items():
                ncOUT.createDimension(dim_name,dim_obj.size)

            ncvar = ncOUT.createVariable(
                "TRN" + var,
                output_dtype,
                ('time','z','y','x'),
                **var_args,
            )
            setattr(ncvar,'missing_value', ncvar._FillValue)
            ncvar[:] = np.asarray(ncIN["TRN" + var][:], dtype=output_dtype)

from pathlib import Path

def compress_nc4(
        input_dir: Path,
        output_dir: Path,
        path_mask: str,
        cut_level: Optional[int] = None,
        var_args: Optional[dict] = None,
        rst_da_var_args: Optional[dict] = None,
        communicator = None
):

    """Compresses NetCDF4 files with optional parallel processing using MPI.

    This function processes NetCDF4 files by applying compression settings and
    writing them to a new location. It handles different file types (ave, RST,
    RST_after, RSTbefore) with specific processing for each type.
    The function can operate in parallel using MPI by distributing files
    across available ranks.

    Args:
        input_dir: Directory containing input NetCDF4 files.
        output_dir: Directory where compressed files will be written.
        path_mask: Glob pattern to match input files (e.g. "*.nc").
        cut_level: Number of depth levels to include in output.
            If None, all levels are kept.
        var_args (dict | None): Dictionary of the arguments that will be
            passed to the netCDF4.createVariable function. Usually it contains
            values like "complevel" and "zlib". Defaults to empty dict if None.
        rst_da_var_args (dict | None): Additional variable creation arguments
            for RST_DA files. These values are added to the var_args dictionary
            when creating the variables of the RST_DA files. If there is a
            conflict, the values of this dictionary are used. Defaults to empty
            dict if None.
        communicator: MPI communicator object for parallel processing.
            If None, the global communicator is used if MPI has been imported,
            otherwise it will run in serial.

    Note:
        The function processes files in parallel when run with MPI,
        distributing files across ranks in a round-robin fashion.
    """
    if communicator is None:
        communicator = get_mpi_communicator()

    if var_args is None:
        var_args = {}

    if rst_da_var_args is None:
        rst_da_var_args = {}

    # Add all the values of var_args to rst_da_var_args
    rst_da_var_args_complete = var_args.copy()
    rst_da_var_args_complete.update(rst_da_var_args)

    rank = communicator.Get_rank()
    nranks = communicator.size

    file_list = sorted(input_dir.glob(path_mask))

    for filename in file_list[rank::nranks]:
        basename = filename.name
        outfile = output_dir / basename

        LOGGER.info("Writing file %s", outfile)

        prefix, datestr, var, _ = basename.rsplit(".")
        if prefix=='ave':
            WRITE_AVE(filename, outfile, var, var_args=var_args)
        if prefix=="RST":
            if datestr.count("0000"):
                WRITE_RST_DA(
                    filename,
                    outfile,
                    var,
                    cut_level,
                    var_args=rst_da_var_args_complete,
                )
            else:
                WRITE_RST(
                    filename,
                    outfile,
                    var,
                    output_dtype=np.float64,
                    var_args=var_args
                )
        if prefix in ["RST_after", "RSTbefore"]:
            WRITE_RST_DA(
                filename,
                outfile,
                var,
                cut_level,
                var_args=rst_da_var_args_complete
            )



def configure_logger(root_logger = None, rank: int = 0) -> None:
    """Configure logging settings for the application.

    Sets up logging with a specific format that includes timestamp,
    rank number, logger name, log level and message. Creates a StreamHandler
    that outputs to stdout and adds it to the root logger.

    Args:
        root_logger: The logger instance to configure. If None, uses the
            module's LOGGER instance. Defaults to None.
        rank: MPI rank number to include in log messages. Useful for
            identifying messages from different processes in parallel
            execution. Defaults to 0.
    """
    if root_logger is None:
        root_logger = LOGGER

    format_string = (
        f"%(asctime)s [rank={rank:0>3}] - %(name)s - "
        "%(levelname)s - %(message)s"
    )
    formatter = logging.Formatter(format_string)

    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    LOGGER.addHandler(handler)


def main():
    args = argument()

    try:
        from mpi4py import MPI
    except Exception:
        LOGGER.info("MPI not available; running in serial")

    comm = get_mpi_communicator()
    configure_logger(rank=comm.Get_rank())

    input_dir  = args.inputdir
    output_dir = args.outputdir
    path_mask = args.filelist
    cut_level = args.cutlevel

    compress_nc4(
        input_dir=input_dir,
        output_dir=output_dir,
        path_mask=path_mask,
        cut_level=cut_level,
        var_args={
            "zlib": True,
            "complevel": 6,
            "fill_value": np.float32(1.0e+20),
        }
    )


if __name__ == '__main__':
    main()
