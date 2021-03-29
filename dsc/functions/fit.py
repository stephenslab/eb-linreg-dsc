#
import numpy as np
import vampyre
from ebmrPy.inference.ebmr import EBMR
import collections


def fit_ebmr_base(X, y, prior = 'point', grr = 'mle', 
             grid = np.array([0.001, 1.0, 2.0, 3.0, 4.0]), 
             ignore_convergence = True):
    n, p = X.shape
    ymean = np.mean(y)
    Xnew  = np.concatenate((np.ones((n, 1)),  X), axis = 1)
    ynew  = y - ymean
    ebmr  = EBMR(Xnew, ynew, prior = prior, grr = grr,
                 sigma = 'full', inverse = 'direct',
                 s2_init = 1.0, sb2_init = 1.0,
                 max_iter = 100, tol = 1e-8,
                 mll_calc = False,
                 mix_point_w = grid,
                 ignore_convergence = True
                )
    ebmr.update()
    intercept = ebmr.mu[0] + ymean
    beta = ebmr.mu[1:]
    ebmr_info = ['s2', 'sb2', 'sigma', 'mu', 'Wbar', 'Wbarinv', 'elbo', 'mll_path', 'elbo_path', 'n_iter', 'mixcoef']
    model = dict()
    for info in ebmr_info:
        model[info] = getattr(ebmr, info)
    return model, intercept, beta


def vamp_solver(X, y, probc, meanc, varc, sigma2_init, max_iter, tune_wvar = True):
    n, p        = X.shape
    bshape      = (p, 1)
    Xop         = vampyre.trans.MatrixLT(X, bshape)
    # flag indicating if the estimator uses MAP estimation (else use MMSE).
    map_est = False
    # Use Gaussian mixture estimator class with auto-tuning
    # Enables EM tuning of the GMM parameters.
    # In this case, probc, meanc and varc are used as initial estimates
    # zvarmin - minimum variance in each cluster
    est_in_em = vampyre.estim.GMMEst(shape = bshape,
                                     zvarmin = 1e-6, tune_gmm = True,
                                     probc = probc, meanc = meanc, varc = varc,
                                     name = 'GMM input')

    est_out_em = vampyre.estim.LinEst(Xop, y, wvar = sigma2_init,
                                      map_est = map_est, tune_wvar = tune_wvar,
                                      name = 'Linear+AWGN')
    # Create the message handler
    msg_hdl = vampyre.estim.MsgHdlSimp(map_est = map_est, shape = bshape)
    # Create the solver
    solver = vampyre.solver.Vamp(est_in_em, est_out_em, msg_hdl, hist_list=['zhat'],
                                 nit = max_iter, prt_period = 0)
    # Run the solver
    solver.solve()
    return solver.hist_dict['zhat']


# Some ad-hoc initialization of the Gaussian Mixture Model (GMM)
def vamp_initialize(X, probc, meanc, varc, sigma2_init):
    n, p         = X.shape
    # How many components?
    if not all(x is None for x in [probc, meanc, varc]):
        clist = [len(x) for x in [probc, meanc, varc] if x is not None]
        ncomp = clist[0]
        assert all(x==clist[0] for x in clist), "Different lengths for initial GMM prob / mean / var"
    else:
        ncomp = 2
    # Proportion of each component
    if not (probc):
        prob_hi   = np.minimum(n / p / 2, 0.95)
        probc     = np.zeros(ncomp)
        probc[1:] = np.repeat(prob_hi / (ncomp - 1), (ncomp - 1))
        probc[0]  = 1 - np.sum(probc[1:])
    # Mean of each component
    if not (meanc):
        meanc     = np.zeros(ncomp)
    # Variance of each component
    if not (varc):
        var_hi    = sigma2_init / (np.mean(np.abs(X)**2) * p * np.sum(probc[1:]))
        var_hi    = max(var_hi, 0.1)
        varc      = var_hi * np.arange(ncomp) / (ncomp - 1)
        varc[0]   = var_hi * 1e-4 # the first component cannot be zero.
    #print (probc)
    #print (meanc)
    #print (varc)
    return probc, meanc, varc
    


def fit_em_vamp(X, y, max_iter = 100,
            probc = None, meanc = None, varc = None, 
            use_intercept = True, try_fixed_wvar = False):

    n, p        = X.shape
    ymean       = np.mean(y)

    # For intercept, add a column of 1s to X
    # redundant because I am also subtracting the mean of y
    if use_intercept:
        Xnew = np.concatenate((np.ones((n, 1)),  X), axis = 1)
        ynew = (y - ymean).reshape(-1, 1)
    else:
        Xnew = np.concatenate((np.zeros((n, 1)), X), axis = 1)
        ynew = y.reshape(-1, 1)

    # Initial sigma2 is set to the variance of y (mean centered).
    sigma2_init = np.mean(ynew**2)

    # Initial probc, meanc, varc
    probc, meanc, varc = vamp_initialize(Xnew, probc, meanc, varc, sigma2_init)

    # Get the estimation history
    has_converged = True
    bhat_hist = vamp_solver(Xnew, ynew, probc, meanc, varc, sigma2_init, max_iter)

    # Tune off the wvar if estimation has not converged
    # These are some random hacks to check if 
    # optimization has converged.
    if try_fixed_wvar:
        if np.isnan(bhat_hist[-1].reshape(-1)).any():
            has_converged = False
        else:
            ypred = np.dot(Xnew, bhat_hist[-1]) + ymean
            if np.sqrt(np.mean((y - ypred)**2)) >= 1e3:
                has_converged = False
        if not has_converged:
            bhat_hist = vamp_solver(Xnew, ynew, probc, meanc, varc, sigma2_init, max_iter, tune_wvar = False)

    if use_intercept:
        for bhat in bhat_hist:
            bhat[0] += ymean
    bopt = bhat_hist[-1].reshape(-1)
    return bhat_hist, bopt[0], bopt[1:], has_converged
