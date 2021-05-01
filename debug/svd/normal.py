import numpy as np

def simulate (n, p):
    X     = np.random.normal(0, 1, size = n * p).reshape(n, p)
    beta  = np.random.normal(0, 1, size = p)
    y     = np.dot(X, beta) + np.random.normal(0, 1, size = n)
    return X, y, beta 

X = np.random.normal(0, 1, size = n * p).reshape(n, p)
