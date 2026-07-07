import argparse
from bitsea.utilities.argparse_types import existing_dir_path
from bitsea.utilities.argparse_types import existing_file_path
from bitsea.utilities.argparse_types import path_inside_an_existing_dir


def argument():
    parser = argparse.ArgumentParser(description = '''
    Creates ave files with aggregated var for aveScan.py. 
    Avescan.py. Creates also chl sup.''')
    parser.add_argument(   '--inputdir', '-i',
                                type = existing_dir_path,
                                required = True,
                                help = '/some/path/MODEL/AVE_FREQ_1/')

    parser.add_argument(   '--tmpdir', '-t',
                                type = path_inside_an_existing_dir,
                                default = None,
                                required = False,
                                help = """ /some/path/POSTPROC/output/AVE_FREQ_1/TMP/ .  
                                Path to put files with aggregated variables for aveScan.py. 
                                No generation of aggregate files if this parameter is omitted.
                                """)
    parser.add_argument(   '--archivedir', '-a',
                                type = path_inside_an_existing_dir,
                                default = None,
                                required=False,
                                help = '''/some/path/POSTPROC/output/AVE_FREQ_1/Archive/  . 
                                Path to put native vars as they are, in order to compress them.
                                No generation of archived files if this parameter is omitted.
                                ''')
    
    parser.add_argument(   '--chlsupdir', '-c',
                                type = path_inside_an_existing_dir,
                                default = None,
                                required=False,
                                help = """/some/path/POSTPROC/output/AVE_FREQ_1/CHL_SUP.
                                No generation of chl sup if this parameter is omitted.
                                """)    
    parser.add_argument(   '--avelist',"-l",
                                type = str,
                                default = "ave*N1p.nc",
                                help = 'ave*.N1p.nc, they configure the date list')
    parser.add_argument(   '--descriptor',"-d",
                                type = existing_file_path,
                                required = True,
                                help = 'VarDescriptor_1.xml, or the complete path')
    parser.add_argument(   '--maskfile',"-m",
                                type = existing_file_path,
                                required = True,
                                help = '''Path of the mask file''')
    parser.add_argument(   '--serial', '-s',
                                action='store_true',
                                help = """Serial mode. No use of mpi4py.
                                """)

    return parser.parse_args()

args = argument()


import logging

import read_descriptor
import GB_lib as G
from bitsea.commons.mask import Mask
from bitsea.utilities.mpi_serial_interface import DummyCommunicator
from bitsea.utilities.mpi_serial_interface import get_mpi_communicator

LOGGER = logging.getLogger()
DATEFORMAT = "%Y%m%d-%H:%M:%S"


if args.serial:
    comm = DummyCommunicator()
else:
    try:
        from mpi4py import MPI
        comm  = get_mpi_communicator()
    except Exception:
        raise ValueError(
            "mpi4py not found; use the -s flag to force serial execution"
        )


def configure_logger(communicator=comm):
    if communicator.size == 1:
        formatter = logging.Formatter(
            "%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
            datefmt=DATEFORMAT
        )
    else:
        formatter = logging.Formatter(
            f"%(asctime)s.%(msecs)03d - rank {communicator.Get_rank():0>3} - %(name)s - "
            f"%(levelname)s - %(message)s",
            datefmt=DATEFORMAT
        )

    LOGGER.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    LOGGER.addHandler(handler)


configure_logger()
AVEDIR  = args.inputdir

RD = read_descriptor.read_descriptor(str(args.descriptor))
if comm.Get_rank() == 0:
    LOGGER.info("INPUT_DIR = %s", AVEDIR)


if args.archivedir:
    ARCHIVEdir = args.archivedir
    if comm.Get_rank() == 0:
        LOGGER.info("ARCHIVEDIR = %s", ARCHIVEdir)
        ARCHIVEdir.mkdir(exist_ok=True)

if args.tmpdir:
    TMPOUTdir  = args.tmpdir
    if comm.Get_rank() == 0:
        LOGGER.info("TMPOUTDIR = %s", TMPOUTdir)
        TMPOUTdir.mkdir(exist_ok=True)

if args.chlsupdir:
    CHLSUPdir  = args.chlsupdir
    if comm.Get_rank() == 0:
        LOGGER.info("CHLSUPDIR = %s", CHLSUPdir)
        CHLSUPdir.mkdir(exist_ok=True)

comm.barrier()

SingleVar_filelist = sorted(AVEDIR.glob(args.avelist))
try:
    TheMask = Mask.from_file(args.maskfile)
except AttributeError:
    TheMask = Mask(args.maskfile)


rank  = comm.Get_rank()
nranks = comm.size
for N1pfile in SingleVar_filelist[rank::nranks]:

    if args.tmpdir:
        G.WriteAggregateAvefiles(
            TheMask,
            str(N1pfile),
            str(AVEDIR) + "/",
            str(TMPOUTdir) + "/",
            str(TMPOUTdir) + "/",
            RD
        )
    
    if args.chlsupdir:
        if not args.tmpdir:
            raise ValueError(
                "tmpdir must be specified if chlsupdir is specified"
            )
        F = G.filename_manager(str(N1pfile))
        chl3dfile = TMPOUTdir / (F.prefix + "." + F.datestr + ".P_l.nc")
        chl2dfile = CHLSUPdir / (F.prefix + "." + F.datestr + ".P_l.nc")
        if str(chl3dfile).find('after')>-1:
           chlvar = 'TRNP_l'
        else:
           chlvar = 'P_l'
        G.writeChlSup(str(chl3dfile), str(chl2dfile), chlvar)
