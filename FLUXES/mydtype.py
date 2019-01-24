#! /usr/bin/python

import numpy as np


trans_dt=np.dtype([('name','S12'),('type','S12'),('lon1',np.float),('lon2',np.float),\
                                                ('lat1',np.float),('lat2',np.float),\
                                                ('depth1',np.float),('depth2',np.float)])


ind2d   =np.dtype([('lat',np.int),('lon',np.int)])


# datatype for fluxes

flux_dt =np.dtype([('adv-u',np.float),('adv-v',np.float),('adv-w',np.float),('sed-w',np.float),\
                   ('hdf-x',np.float),('hdf-y',np.float),('zdf-z',np.float)])

