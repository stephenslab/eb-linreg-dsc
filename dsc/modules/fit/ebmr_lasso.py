# This python script implements the "ebmr_lasso" module.
from fit import fit_ebmr_base
model, mu, beta = fit_ebmr_base(X, y, prior='dexp')

