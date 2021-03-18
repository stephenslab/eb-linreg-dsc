#
import simulate
import dsc_io

n, p, s = dsc_io.read_sim_input_params(dims, sfrac)
X, y, Xtest, ytest, beta, sigma = simulate.equicorr_predictors (n, p, s, pve, signal = signal, seed = None, rho = rho, bfix = bfix)
