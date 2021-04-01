# This python script implements the "em_vamp_ash" module.
from fit import fit_em_vamp
import numpy as np

ncomp    = 20
probc    = None
meanc    = np.zeros(ncomp)
varc     = (4**(np.arange(ncomp)/ncomp) - 1)**2
varc[0]  = 1e-4
mean_fix = np.ones(ncomp)
var_fix  = np.ones(ncomp)
model, mu, beta = fit_em_vamp(X, y, probc = probc, meanc = meanc, varc  = varc, 
                              mean_fix = mean_fix, var_fix  = var_fix)

