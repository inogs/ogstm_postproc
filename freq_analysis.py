import matplotlib
matplotlib.use('Qt5Agg')
import pylab as pl
import numpy as np
from numpy.fft import fft, ifft


def aliasing_test(T=26):
    '''
    T is the period of the signal expressed in hours
    '''


    t=np.arange(2600)
    f = np.sin(2*np.pi/T * t)
    
    fig,ax=pl.subplots()
    ax.plot(t,f)
    fig.show()
    
    p=24
    n_iterations=len(t)/p
    M = np.zeros((n_iterations), np.float32)
    
    for i in range(n_iterations):
        istart=(i-1)*p
        iend = i*p
        M[i] = f[istart:iend].mean()
        
    fig,ax=pl.subplots()
    ax.plot(M)
    ax.grid()
    fig.show()


    # T 28h: 7days
    # T 27h : 9 days
    # T 26h : 13 days
    # T 25h : 25 days

from bitsea.timeseries.plot import read_pickle_file

my_dytype=[('varname','U10'),('xlim_max',np.float32),('ylim_max',np.float32)]

PLOTS=np.zeros((2), dtype=my_dytype)
PLOTS[0]=('sossheig',0.1,300)
PLOTS[1]=('Energy',0.2, 25)

ivar=1
varname=PLOTS[ivar]['varname']
INPUTDIR='/g100_scratch/userexternal/gbolzon0/BI-HOURLY/2H/PROFILES/'

pklfile="%s%s.pkl" %(INPUTDIR,varname)
A,TL = read_pickle_file(pklfile)

OUTDIR="/g100_work/OGS_devC/gbolzon/BI-HOURLY/POSTPROC/IMG/"
nPoints=4
idepth = 0

for iPoint in range(nPoints):
    outfile = "%sFreqSpectrum.%02d.%s.png" %(OUTDIR,iPoint,varname)
    print(outfile)
    ts = A[:,iPoint,idepth]
    
    X = fft(ts)
    
    #sampling rate
    sr=0.5 # hours
    N = len(ts)
    T = N/sr  # 4382*2=8764
    n = np.arange(N)
    freq = n/T  # 0-->0.5
    
    pl.close('all')
    fig,ax = pl.subplots()
    fig.set_size_inches(10,3)
    ax.stem(freq,np.abs(X))
    
    fig.suptitle(varname)
    ax.set_xlim([0,PLOTS[ivar]['xlim_max']])
    ax.set_ylim([0,PLOTS[ivar]['ylim_max']])
    ax.grid()
    ax.set_position([0.1, 0.18, 0.8, 0.7])
    ax.set_xlabel('Freq (1/h)')
    ax.set_ylabel('FFT Amplitude |X(freq)|')
    
    #fig.show()
    fig.savefig(outfile)