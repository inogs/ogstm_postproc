import argparse
import logging

import numpy as np
from bitsea.utilities.argparse_types import existing_dir_path
from bitsea.utilities.mpi_serial_interface import get_mpi_communicator

from netcdf4_compress import compress_nc4
from netcdf4_compress import configure_logger


if __name__ == '__main__':
    LOGGER = logging.getLogger()
else:
    LOGGER = logging.getLogger(__name__)


def argument():
    parser = argparse.ArgumentParser(description = '''
    Generates netCDF4 compressed files

    Parallel executable, can be called by mpirun.
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
    parser.add_argument(   '--significant_digits',"-s",
                                required= False,
                                type = int,
                                default = 2,
                                help = 'depth levels on output files')
 
    return parser.parse_args()


def main():
    args = argument()

    try:
        from mpi4py import MPI
    except Exception:
        LOGGER.info("MPI not available; running in serial")

    comm = get_mpi_communicator()
    configure_logger(root_logger=LOGGER, rank=comm.Get_rank())

    input_dir = args.inputdir
    output_dir = args.outputdir
    path_mask = args.filelist
    cut_level = args.cutlevel
    significant_digits = args.significant_digits

    compress_nc4(
        input_dir=input_dir,
        output_dir=output_dir,
        path_mask=path_mask,
        cut_level=cut_level,
        var_args={
            "zlib": True,
            "complevel": 9,
            "fill_value": np.float32(1.0e+20),
            "least_significant_digit": significant_digits
        },
        rst_da_var_args = {
            "least_significant_digit": 3,
        }
    )


if __name__ == '__main__':
    main()
