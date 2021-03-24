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
    simulate:  indepgauss, equicorrgauss
    fit:       ridge, lasso, elastic_net,
               lasso_1se, elastic_net_1se, scad, mcp, l0learn,
               susie, varbvs, varbvsmix, blasso, bayesb,
               mr_ash, mr_ash_init
    predict:   predict_linear
    score:     mse, mae
  run: 
    all:       simulate * fit * predict * score


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
  dims:    R{list(c(n=500, p=200),
                  c(n=100, p=200))}
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

# Fit a "sum of single effects" (SuSiE) regression model.
susie (fitparams):           susie.R

# Compute a fully-factorized variational approximation for Bayesian
# variable selection in linear regression (varbvs).
varbvs (fitparams):          varbvs.R

# This is a variant on the varbvs method in which the "spike-and-slab"
# prior on the regression coefficients is replaced with a
# mixture-of-normals prior.
varbvsmix (fitparams):       varbvsmix.R


# Fit using SCAD and MCP penalties
scad (fitparams):            scad.R
mcp (fitparams):             mcp.R

# Fit L0Learn
l0learn (fitparams):         l0learn.R

# Fit Bayesian Lasso
blasso (fitparams):          blasso.R

# Fit BayesB
bayesb (fitparams):          bayesb.R


# Fit Mr.ASH
# This is an abstract base class, which contains all default values.
# Several variations of Mr.ASH use this abstract base class (see below).
mr_ash_base (fitparams):     mr_ash.R
  grid:          NULL
  init_pi:       NULL
  init_beta:     NULL
  init_sigma2:   NULL
  update_pi:     TRUE
  update_sigma2: TRUE
  update_order:  NULL

# This is the default variant of Mr.ASH
mr_ash (mr_ash_base):
  grid:          (2^((0:19)/20) - 1)^2

# This is the variant used by Youngseok Kim
# in his simulation pipeline for producing 
# the figures in the manuscript (as on 2021-03-18).
# (??)
# Essentially, this is a "spike-and-slab" prior
# initialized with simulation parameters.
# Although results are very similar to the default variant of Mr.ASH,
# this should not be used for the manuscript.
# 
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
