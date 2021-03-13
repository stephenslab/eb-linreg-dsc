# A DSC for evaluating prediction accuracy of multiple linear regression
# methods in different scenarios.
# This is designed to reproduce the results of the manuscript of Mr. Ash by Kim, Wang, Carbonetto and Stephens
DSC:
  python_modules: numpy
  lib_path: functions
  exec_path: modules/simulate
  output: dsc_result
  define:
    simulate: indepgauss, equicorrgauss, changepoint, one_changepoint
  run: simulate

# simulate modules
# ===================

simparams:
# Abstract module for simulation.
# Common input parameters and output data for all simulation designs.
# sfix:  Number of predictors with non-zero coefficients.
#        If sfix is not set / None, then the number is calculated dynamically from sfrac.
# sfrac: Fraction of predictors which have non-zero coefficients
# signal: distribution of the coefficients for the non-zero predictors
#    - "normal": Gaussian(mean = 0, sd = 1)
#    - "fixed":  Use pre-defined value(s) of beta
#                bfix: sequence / float of predefined beta
#                (if sequence, length must be equal to number of non-zero coefficients).
# snr: signal-to-noise ratio
  seed:    100
  dims:    R{list(c(n=100, p=200), 
                  c(n=200, p=200),
                  c(n=200, p=100))}
  sfix:    None
  sfrac:   0.1
  bfix:    None
  signal:  "normal"
  $X:      X
  $y:      y
  $Xtest:  Xtest
  $ytest:  ytest
  $beta:   beta
  $se:     sigma

equicorrgauss(simparams): equicorrgauss.py
  rho:     0.8
  pve:     0.7

indepgauss(equicorrgauss):
  rho:    0.0

changepoint(simparams): changepoint.py
  snr:    10

one_changepoint(changepoint):
  sfix:   1
  signal: "fixed"
  bfix:   8
