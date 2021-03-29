# This python script implements the "em_vamp" module.
from fit import fit_em_vamp
model, mu, beta, converged = fit_em_vamp(X, y, use_intercept = True)

