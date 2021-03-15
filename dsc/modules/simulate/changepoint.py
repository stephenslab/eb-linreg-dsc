#
import simulate
import dsc_io

n, p, s = dsc_io.read_sim_input_params (dims, sfrac = sfrac, sfix = sfix)
X, y, Xtest, ytest, beta, sigma = simulate.changepoint_predictors (n, p, s, snr, signal = signal, seed = seed, bfix = bfix)
