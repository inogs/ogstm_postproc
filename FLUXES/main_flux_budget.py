import flux_budget_lib as fbl



datadir='/Users/plazzari/Documents/workspace/Paolo_TOOLS/FLUXES/TRANSECTS/DATA/GSMED-01/' # SO-03



#VARlist=['POVc','POVp','POVn','POVs','POMc','POMp','POMn','POMs','DOMc','DOMp','DOMn','REFc','DIC_','DIP_','DIN_','DIS_','ALK_'];
VARlist=['DIP_','DIN_']

dStart= 0
dEnd  = 5000

for VAR in VARlist:
    print VAR
    fbl.flux_budget(VAR, dStart, dEnd, datadir)

dStart= 0
dEnd  = 180

for VAR in VARlist:
    print VAR
    fbl.flux_budget(VAR, dStart, dEnd, datadir)

dStart= 180
dEnd  = 750

for VAR in VARlist:
    print VAR
    fbl.flux_budget(VAR, dStart, dEnd, datadir)

dStart= 750
dEnd  = 5000

for VAR in VARlist:
    print VAR
    fbl.flux_budget(VAR, dStart, dEnd, datadir)


