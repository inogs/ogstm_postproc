import sys
sys.path.insert(0, '/marconi_scratch/userexternal/ggalli00/CLIMA_100/PLOT_SCRIPTS')

import flux_across_transect_lib as fbl



datadir='/marconi_scratch/userexternal/ggalli00/CLIMA_100/TR-PO4-O2-R7c/wrkdir/MODEL/FLUXES_FULL/'



#VARlist=['POVc','POVp','POVn','POVs','POMc','POMp','POMn','POMs','DOMc','DOMp','DOMn','REFc','DIC_','DIP_','DIN_','DIS_','ALK_'];
VARlist=['N1p','N3n', 'O2o','R1c','R2c','R6c','R7c','O3h','O3c']


for VAR in VARlist:
    print VAR
    fbl.flux_across_transect(VAR, datadir)





