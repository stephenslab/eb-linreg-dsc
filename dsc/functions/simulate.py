import numpy as np
import collections
from sos.utils import env

def parse_input_params(dims, sfrac=0.5, sfix=None):
    n = dims[0]
    p = dims[1]
    if sfix is not None:
        s = sfix
    else:
        s = max(1, int(sfrac * p))
    return n, p, s

def sample_betas (p, bidx, method="normal", bfix=None):
    beta = np.zeros(p)
    s = bidx.shape[0]

    # sample beta from Gaussian(mean = 0, sd = 1)
    if method == "normal":
        beta[bidx] = np.random.normal(size = s)

    # receive fixed beta input
    elif method == "fixed":
        assert bfix is not None, "bfix is not specified for fixed signal"
        if isinstance(bfix, (collections.abc.Sequence, np.ndarray)):
            assert len(bfix) == s, "Length of input coefficient sequence is different from the number of non-zero coefficients"
            beta[bidx] = bfix
        else:
            beta[bidx] = np.repeat(bfix, s)

    return beta


def get_responses (X, b, sd):
    return np.dot(X, b) + sd * np.random.normal(size = X.shape[0])


def get_sd_from_pve (X, b, pve):
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
    bidx  = np.random.choice(p, s, replace = False)
    beta  = sample_betas(p, bidx, method = signal, bfix = bfix)
    # obtain sd from pve
    se    = get_sd_from_pve(X, beta, pve)
    # calculate the responses
    y     = get_responses(X,     beta, se)
    ytest = get_responses(Xtest, beta, se)
    return X, y, Xtest, ytest, beta, se


def changepoint_predictors (n, p, s, snr, k = 0, signal = "normal", seed = None, bfix = None, center_sticky = True):
    '''
    Trend-filtering data. 
    '''
    X     = trend_filtering_basis(n, p, k)
    Xtest = X.copy()
    # sample betas
    m = min(n, p)
    imin = k + 1
    imax = m
    # if we want the change at the center of the data.
    if s == 1 and center_sticky:
        if n > p:
            imax = min(imax, 2 * int(n / 3))
            imin = max(imin, int (imax / 2))
        bidx = np.array([int((imin + imax)/2)])
    else:
        bidx  = np.random.choice(np.arange(imin, imax), s, replace = False)
    # obtain values of beta
    beta  = sample_betas(p, bidx, method = signal, bfix = bfix)
    # obtain sd from signal-to-noise ratio
    se    = np.max(np.abs(beta)) / snr
    # calculate the responses
    y     = get_responses(X,     beta, se)
    ytest = get_responses(Xtest, beta, se)
    return X, y, Xtest, ytest, beta, se


def trend_filtering_basis(n, p, k):
    '''
    adapted from [Tibshirani, 2014](https://doi.org/10.1214/13-AOS1189)
    Equation (22) [page 303]
    '''
    m = min(n, p)
    X = np.zeros((m, m))
    if k == 0:
        for j in range(m):
            X[j:m, j] = 1
    else:
        # j = 1, ..., k+1
        seq = np.arange(1, m+1).reshape(m,1)
        X[:, :k + 1] = np.power(np.tile(seq, k+1), np.arange(k+1)) / np.power(m, np.arange(k+1))
        # j > k + 1
        for j in range(k+1, m):
            khalf = int(k / 2) if k % 2 == 0 else int((k + 1) / 2)
            X[(j - khalf + 1):, j] = np.power(np.arange(j - khalf + 1, m) - j + khalf, k) / np.power(m, k)
    G = np.zeros((n, p))
    if n >= p:
        G[:p, :] = X
    else:
        G[:, :n] = X
    return G


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
