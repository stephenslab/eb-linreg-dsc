import numpy as np
import collections
from sos.utils import env

def sample_betas(p, s, method="normal", bfix=None):
    beta = np.zeros(p)
    bidx = np.random.choice(p, s, replace = False)

    # sample beta from Gaussian(mean = 0, sd = 1)
    if method == "normal":
        beta[bidx] = np.random.normal(size = s)

    # receive fixed beta input
    elif method == "fixed":
        assert bfix is not None, "bfix is not specified for fixed signal"
        if isinstance(bfix, (collections.abc.Sequence, np.ndarray)):
            assert len(bfix) == 4, "Length of input coefficient sequence is different from the number of non-zero coefficients"
            beta[bidx] = bfix
        else:
            beta[bidx] = np.repeat(bfix, s)

    return beta


def sample_betas_fixtrend(p, s, bfix):
    '''
    a special trend filtering where non-zero coefficients appear in pairs,
    i.e. for every non-zero coefficient b for m-th predictor,
    the coefficient for (m+1)-th predictor should be -b.
    Hence, y becomes a step function of X * beta when X is a changepoint predictor.
    for example, beta = [ 0 0 0 b1 -b1 0 0 0 0 b2 -b2 0 0 0 ... ]
    '''
    assert bfix is not None, "bfix is not specified for fixed signal"
    beta = np.zeros(p)
    # since every non-zero coefficient appear in pairs,
    # total number of non-zero coefficients must be even.
    # If input s is odd, it is silently forced to become even 
    # TO DO: Throw error for odd value of s
    nc   = max(1, int(s / 2))
    bidx = np.random.choice(p - 1, nc, replace = False)
    # create non-zero sequence of beta
    if isinstance(bfix, (collections.abc.Sequence, np.ndarray)):
        env.logger.info("Sequence value of bfix.")
        assert len(bfix) == nc, "For fixtrend, length of input coefficient sequence must be half of the number of non-zero coefficients"
        nonzerob = bfix.copy()
    else:
        env.logger.info("Float value of bfix.")
        nonzerob = np.repeat(bfix, nc)
    # update beta
    beta[bidx]     = nonzerob
    beta[bidx + 1] = -nonzerob
    return beta


def get_responses(X, b, sd):
    return np.dot(X, b) + sd * np.random.normal(size = X.shape[0])


def get_sd_from_pve(X, b, pve):
    return np.sqrt(np.var(np.dot(X, b)) * (1 - pve) / pve)
    

def equicorr_predictors (n, p, s, pve, signal = "normal", seed = None, rho = 0.5, bfix = None):
    '''
    X is sampled from a multivariate normal, with covariance matrix S.
    S has unit diagonal entries and constant off-diagonal entries rho.
    '''
    iidX  = np.random.normal(size = n * 2 * p).reshape(n * 2, p)
    comR  = np.random.normal(size = n * 2).reshape(n * 2, 1)
    Xall  = comR * np.sqrt(rho) + iidX * np.sqrt(1 - rho)
    # split into training and test data
    X     = Xall[:n, :]
    Xtest = Xall[n:, :]
    # sample betas
    beta  = sample_betas(p, s, method = signal, bfix = bfix)
    # obtain sd from pve
    se    = get_sd_from_pve(X, beta, pve)
    # calculate the responses
    y     = get_responses(X,     beta, se)
    ytest = get_responses(Xtest, beta, se)
    return X, y, Xtest, ytest, beta, se


def changepoint(n, p, s, snr, signal = "normal", seed = None, bfix = None):
    '''
    Trend-filtering data. 
    '''
    X = np.zeros((n, p))
    #for i in range(p):
    #    X[i:n, i] = np.arange(1, n - i + 1)
    for j in range(min(n, p)):
        for i in range(j+1, n):
            X[i, j] = 1
    Xtest = X.copy()
    # sample betas
    beta = sample_betas(p, s, method = signal, bfix = bfix)
    # obtain sd from signal-to-noise ratio
    se    = np.max(np.abs(beta)) / snr
    # calculate the responses
    y     = get_responses(X,     beta, se)
    ytest = get_responses(Xtest, beta, se)
    return X, y, Xtest, ytest, beta, se
