#
import simulate

n, p, s = simulate.parse_input_params (dims, sfix = sfix)
X, y, Xtest, ytest, beta, sigma = simulate.changepoint_predictors (n, p, s, snr, k = basis_k, signal = signal, seed = None, bfix = bfix, center_sticky = True)
