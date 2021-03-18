# A DSC for evaluating prediction accuracy of 
# multiple linear regression methods in different scenarios.

# A DSC for evaluating prediction accuracy of multiple linear regression
# methods in different scenarios.
# This is designed to reproduce the results of the manuscript of Mr. Ash by Kim, Wang, Carbonetto and Stephens
DSC:
  R_libs:    MASS, 
             glmnet, 
             susieR, 
             varbvs >= 2.6-3,
             mr.ash.alpha,
             L0Learn,
             BGLR,
             ncvreg
  python_modules: numpy
  lib_path:  functions
  exec_path: modules/simulate,
             modules/fit,
             modules/predict,
             modules/score
  output: dsc_result
  replicate: 20
  define:
    #simulate: indepgauss, equicorrgauss, changepoint, one_changepoint
    simulate: indepgauss, equicorrgauss
    fit:      ridge, lasso, lasso_1se, elastic_net, elastic_net_1se,
              scad, mcp,
              mr_ash, mr_ash_init
    predict:  predict_linear
    score:    mse, mae
  run: 
    all:      simulate * fit * predict * score
    select:   simulate * ( mr_ash, scad ) * predict * score


# simulate modules
# ===================

simparams:
# This is an abstract module for simulation.
# Input parameters and output data for all simulation designs.
#
# sfix:  Number of predictors with non-zero coefficients.
#        If sfix is not set / None, then the number is calculated dynamically from sfrac.
# sfrac: Fraction of predictors which have non-zero coefficients
# signal: distribution of the coefficients for the non-zero predictors
#    - "normal": Gaussian(mean = 0, sd = 1)
#    - "fixed":  Use pre-defined value(s) of beta
#                bfix: sequence / float of predefined beta
#                (if sequence, length must be equal to number of non-zero coefficients).
# pve: proportion of variance explained (required for equicorrgauss.py)
# snr: signal-to-noise ratio (required for changepoint.py)
  dims:    R{list(c(n=500, p=200))}
                  #c(n=200, p=200),
                  #c(n=200, p=100))}
  sfix:    None
  sfrac:   0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0
  bfix:    None
  signal:  "normal"
  $X:      X
  $y:      y
  $Xtest:  Xtest
  $ytest:  ytest
  $n:      n
  $p:      p
  $s:      s
  $beta:   beta
  $se:     sigma

equicorrgauss(simparams): equicorrgauss.py
  rho:     0.95
  pve:     0.5, 0.95

indepgauss(simparams):    equicorrgauss.py
  rho:     0.0
  pve:     0.5, 0.95

changepoint(simparams):   changepoint.py
  snr:     10
  sfix:    1
  signal:  "fixed"
  bfix:    8


# fit modules
# ===================
# All fit modules must have these inputs and outputs
# Extra inputs and outputs can be specified in 
# respective submodules.
fitparams:
  X:          $X
  y:          $y
  $intercept: out$mu
  $beta_est:  out$beta
  $model:     out 

# Fit a ridge regression model using glmnet. The penalty strength
# (i.e., the normal prior on the coefficients) is estimated using
# cross-validation.
ridge (fitparams):           ridge.R
  
# Fit a Lasso model using glmnet. The penalty strength ("lambda") is
# estimated via cross-validation.
lasso (fitparams):           lasso.R
lasso_1se (fitparams):       lasso_1se.R

# Fit an Elastic Net model using glmnet. The model parameters, lambda
# and alpha, are estimated using cross-validation.
elastic_net (fitparams):     elastic_net.R
elastic_net_1se (fitparams): elastic_net_1se.R

# Fit using SCAD and MCP penalties
scad (fitparams):            scad.R
mcp (fitparams):             mcp.R

# Fit mr.ash 
# The base class contains all default values.
# Different options of mr.ash modifies 
# some of these input parameters
mr_ash_base (fitparams):     mr_ash.R
  grid:          NULL
  init_pi:       NULL
  init_beta:     NULL
  init_sigma2:   NULL
  update_pi:     TRUE
  update_sigma2: TRUE
  update_order:  NULL

# And here are the different modifications of mr.ash
mr_ash (mr_ash_base):
  grid:          (2^((0:19)/20) - 1)^2

mr_ash_init (mr_ash_base):
  p:             $p
  s:             $s
  se:            $se
  grid:          c(0, 1 / s)
  init_sigma2:   se^2
  init_pi:       c(1 - s/p, s/p)
  update_pi:     FALSE


# predict modules
# ===============
# A "predict" module takes as input a fitted model (or the parameters
# of this fitted model) and an n x p matrix of observations, X, and
# returns a vector of length n containing the outcomes predicted by
# the fitted model.

# Predict outcomes from a fitted linear regression model.
predict_linear: predict_linear.R
  X:         $Xtest
  intercept: $intercept
  beta:      $beta_est
  $yest:     y   


# score modules
# =============
# A "score" module takes as input a vector of predicted outcomes and a
# vector of true outcomes, and outputs a summary statistic that can be
# used to evaluate accuracy of the predictions.

# Compute the mean squared error summarizing the differences between
# the predicted outcomes and the true outcomes.
mse: mse.R
  y:    $ytest
  yest: $yest
  $err: err 

# Compute the mean absolute error summarizing the differences between
# the predicted outcomes and the true outcomes.
mae: mae.R
  y:    $ytest
  yest: $yest
  $err: err 
