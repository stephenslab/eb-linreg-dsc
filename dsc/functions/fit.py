#
import numpy as np
import vampyre
from ebmrPy.inference.ebmr import EBMR
from ebmrPy.inference.iridge import IRidge
import collections


def fit_ebmr_base(X, y, prior = 'point', grr = 'mle', 
             grid = np.array([0.001, 1.0, 2.0, 3.0, 4.0]), 
             ignore_convergence = True):
    # EBMR does not add intercept
    # Hence, adding an extra column of 1 to X
    Xc, yc, y0 = add_intercept_column(X, y)
    ebmr       = EBMR(Xc, yc, prior = prior, grr = grr,
                      sigma = 'full', inverse = 'direct',
                      s2_init = 1.0, sb2_init = 1.0,
                      max_iter = 100, tol = 1e-8,
                      mll_calc = False,
                      mix_point_w = grid,
                      ignore_convergence = True
                     )
    ebmr.update()
    intercept  = ebmr.mu[0] + y0
    beta       = ebmr.mu[1:]
    # Convert the Python class to dictionary
    model = class_to_dict(ebmr, 
        ['s2', 'sb2', 'sigma', 'mu', 'Wbar', 'Wbarinv', 
         'elbo', 'mll_path', 'elbo_path', 'n_iter', 'mixcoef'])
    return model, intercept, beta


def fit_iridge(X, y, max_iter = 1000):
    Xc, yc, y0 = add_intercept_column(X, y)
    iridge     = IRidge(Xc, yc, max_iter = max_iter)
    iridge.update()
    intercept  = iridge.beta[0] + y0
    beta       = iridge.beta[1:]
    # Convert the Python class to dictionary
    model  = class_to_dict(iridge, 
        ['s2', 'sb2', 'sw2', 'beta', 'mll_path', 'n_iter'])
    return model, intercept, beta


def fit_em_vamp(X, y, max_iter = 100,
            probc = None, meanc = None, varc = None,
            mean_fix = None, var_fix = None):

    n, p        = X.shape
    # For intercept, add a column of 1s to X
    # redundant because I am also subtracting the mean of y
    Xc, yc, y0  = add_intercept_column(X, y)

    # Initial sigma2 is set to the variance of y (mean centered).
    sigma2_init = np.mean(yc**2)

    # Initial probc, meanc, varc
    probc, meanc, varc = vamp_initialize(Xc, probc, meanc, varc, sigma2_init)

    # Get the estimation history
    # has_converged = True
    solver = vamp_solver(Xc, yc.reshape(-1, 1), probc, meanc, varc, sigma2_init, max_iter, 
                         mean_fix = mean_fix, var_fix = var_fix)
    bhat_hist = solver.hist_dict['zhat']

    ## # Tune off the wvar if estimation has not converged
    ## if try_fixed_wvar:
    ##     # These are some random hacks to check if 
    ##     # optimization has converged.
    ##     bopt = bhat_hist[-1]
    ##     if np.isnan(bopt.reshape(-1)).any():
    ##         has_converged = False
    ##     else:
    ##         ypred = np.dot(Xc, bopt) + y0
    ##         if np.sqrt(np.mean((y - ypred)**2)) >= 1e3:
    ##             has_converged = False
    ##     # The above checks does not gurantee convergence
    ##     # but still they might indicate that the gradient descent 
    ##     # has not converged.
    ##     if not has_converged:
    ##         bhat_hist = vamp_solver(Xc, yc, probc, meanc, varc, sigma2_init, max_iter, tune_wvar = False)

    for bhat in bhat_hist:
        bhat[0] += y0
    bopt = bhat_hist[-1].reshape(-1)
    return bhat_hist, bopt[0], bopt[1:]


def vamp_solver(X, y, probc, meanc, varc, sigma2_init, max_iter, 
                tune_wvar = True, tune_gmm = True, mean_fix = None, var_fix = None):
    n, p        = X.shape
    bshape      = (p, 1)
    Xop         = vampyre.trans.MatrixLT(X, bshape)
    # flag indicating if the estimator uses MAP estimation (else use MMSE).
    map_est     = False
    # Use Gaussian mixture estimator class with auto-tuning
    # Enables EM tuning of the GMM parameters.
    # In this case, probc, meanc and varc are used as initial estimates
    # zvarmin - minimum variance in each cluster
    est_in_em   = vampyre.estim.GMMEst(shape = bshape,
                                       zvarmin = 1e-6, tune_gmm = True,
                                       probc = probc, meanc = meanc, varc = varc,
                                       name = 'GMM input', mean_fix = mean_fix, var_fix = var_fix)

    est_out_em  = vampyre.estim.LinEst(Xop, y, wvar = sigma2_init,
                                       map_est = map_est, tune_wvar = tune_wvar,
                                       name = 'Linear+AWGN')
    # Create the message handler
    msg_hdl     = vampyre.estim.MsgHdlSimp(map_est = map_est, shape = bshape)
    # Create the solver
    solver      = vampyre.solver.Vamp(est_in_em, est_out_em, msg_hdl, hist_list=['zhat'],
                                      nit = max_iter, prt_period = 0)
    # Run the solver
    solver.solve()
    return solver


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
    if probc is None:
        prob_hi   = np.minimum(n / p / 2, 0.95)
        probc     = np.zeros(ncomp)
        probc[1:] = np.repeat(prob_hi / (ncomp - 1), (ncomp - 1))
        probc[0]  = 1 - np.sum(probc[1:])
    # Mean of each component
    if meanc is None:
        meanc     = np.zeros(ncomp)
    # Variance of each component
    if varc is None:
        var_hi    = sigma2_init / (np.mean(np.abs(X)**2) * p * np.sum(probc[1:]))
        var_hi    = max(var_hi, 0.1)
        varc      = var_hi * np.arange(ncomp) / (ncomp - 1)
        varc[0]   = var_hi * 1e-4 # the first component cannot be zero.
    #print (probc)
    #print (meanc)
    #print (varc)
    return probc, meanc, varc

# This is a placeholder until I find a proper
# dict converter of the class.
# [(p, type(getattr(classname, p))) for p in dir(classname)]
# shows the types, but how to extract the @property methods?
def class_to_dict(classname, property_list):
    model = dict()
    for info in property_list:
        model[info] = getattr(classname, info)
    return model


def add_intercept_column(X, y):
    n, p  = X.shape
    ymean = np.mean(y)
    Xnew  = np.concatenate((np.ones((n, 1)),  X), axis = 1)
    ynew  = y - ymean
    return Xnew, ynew, ymean
