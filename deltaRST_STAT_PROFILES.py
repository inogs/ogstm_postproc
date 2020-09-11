import argparse

def argument():
    parser = argparse.ArgumentParser(description = '''
    Calculate and write the differences of the mean between two
    pkl stat_profile
    (Useful for DA increments)''')
    parser.add_argument(   '--inputbef', '-b',
                                type = str,
                                required = True,
                                help = 'Input with before pkl')

    parser.add_argument(   '--inputaft', '-a',
                                type = str,
                                required = True,
                                help = 'Input with after pkl')

    parser.add_argument(   '--outdir', '-o',
                                type = str,
                                required = True,
                                help = 'Outdir for diff pkl')

    return parser.parse_args()

args = argument()

import numpy as np
import pickle as pkl
import os,glob
from commons.utils import addsep


IN_BEFORE=addsep(args.inputbef)
IN__AFTER=addsep(args.inputaft)

OUTDIR = addsep(args.outdir)

pklLIST = glob.glob(IN_BEFORE + '/STAT_PROFILES/*.pkl')
VARLIST = [os.path.basename(f)[0:3] for f in pklLIST]


for var in VARLIST:
    print var
    filebef = IN_BEFORE + '/STAT_PROFILES/' + var + '.pkl'
    fid = open(filebef,'r')
    varbef = pkl.load(fid)
    fid.close()

    fileaft = IN__AFTER + '/STAT_PROFILES/' + var + '.pkl'
    if not(os.path.exists(fileaft)):
        print var + '.pkl does not exist in ' + IN__AFTER + '/STAT_PROFILES/'
        print ' CONTINUE on other variables'
        continue
    fid = open(fileaft,'r')
    varaft = pkl.load(fid)
    fid.close()

    TLbef = varbef[1]
    TLaft = varaft[1]

    if not(TLbef.nTimes==TLaft.nTimes):
        print 'Timelists after and before do not have the same lenght EXIT'
        import sys
        sys.exit(0)
    for ii,dd in enumerate(TLbef.Timelist):
        if not(dd==TLaft.Timelist[ii]):
            print 'Different dates at %s element of TLbef w.r.t. TLaft EXIT'
            import sys
            sys.exit(0)


    varINC = [[] for i in range(2)]
    varINC[1] = TLbef
    varINC[0] = varaft[0][:,:,:,:,0] - varbef[0][:,:,:,:,0] #only the average


    fileout = OUTDIR + var + '.pkl'
    fid = open(fileout,'wb')
    pkl.dump(varINC,fid)
    fid.close()
