#'
if (exists("standardize")) {
  if (is.logical(standardize)) {

  } else {
    warning("standardize must be logical: set to FALSE")
    standardize     = FALSE
  }
} else {
  standardize       = FALSE
}

#'
#'
#'
get_phi <- function(fit) {
  # compute residual
  r            = fit$data$y - fit$data$X %*% fit$beta

  # compute bw and S2inv
  bw           = as.vector((t(fit$data$X) %*% r) + fit$data$w * fit$beta)
  S2inv        = 1 / outer(fit$data$w, 1/fit$data$sa2, '+');

  # compute mu, phi
  mu           = bw * S2inv;
  phi          = -log(1 + outer(fit$data$w, fit$data$sa2))/2 + mu * (bw / 2 / fit$sigma2);
  phi          = c(fit$pi) * t(exp(phi - apply(phi,1,max)));
  phi          = t(phi) / colSums(phi);
  return (list(phi = phi, mu = mu, r = r))
}

#'
#'
#'
#' MR.ASH
fit.mr.ash = function(X, y, X.test, y.test, seed = 1, sa2 = NULL) {

  # set seed
  set.seed(seed)

  # run mr.ash
  t.mr.ash           = system.time(
    fit.mr.ash        <- mr.ash(X = X, y = y, sa2 = sa2,
                                max.iter = 2000,
                                standardize = standardize,
                                tol = list(epstol = 1e-12, convtol = 1e-8)))
  beta               = fit.mr.ash$beta
  pip                = 1 - get_phi(fit.mr.ash)$phi[,1]

  return (list(fit = fit.mr.ash, t = t.mr.ash[3], beta = beta, pip = pip,
               rsse = norm(y.test - predict(fit.mr.ash, X.test), '2')))
}

#'
#'
#'
#' MR.ASH different sigma2 update
fit.mr.ash.sigma2 = function(X, y, X.test, y.test, beta.init = NULL, update.order = NULL,
                             seed = 1, sa2 = NULL) {

  # set seed
  set.seed(seed)

  # run mr.ash
  t.mr.ash           = system.time(
    fit.mr.ash        <- mr.ash(X = X, y = y, sa2 = sa2, method = "sigma",
                                max.iter = 2000, beta.init = beta.init,
                                update.order = update.order,
                                standardize = standardize,
                                tol = list(epstol = 1e-12, convtol = 1e-8)))
  beta               = fit.mr.ash$beta
  pip                = 1 - get_phi(fit.mr.ash)$phi[,1]

  return (list(fit = fit.mr.ash, t = t.mr.ash[3], beta = beta, pip = pip,
               rsse = norm(y.test - predict(fit.mr.ash, X.test), '2')))
}

#'
#'
#'
#' MR.ASH
fit.mr.ash2 = function(X, y, X.test, y.test, seed = 1,
                       sa2 = NULL,
                       update.pi = TRUE, pi = NULL,
                       beta.init = NULL, sigma2 = NULL,
                       update.order = NULL) {


  # set seed
  set.seed(seed)

  # run mr.ash order
  t.mr.ash           = system.time(
    fit.mr.ash        <- mr.ash(X = X, y = y, sa2 = sa2, update.order = update.order,
                                max.iter = 2000, min.iter = 200,
                                beta.init = beta.init, update.pi = update.pi, pi = pi,
                                standardize = standardize, sigma2 = sigma2,
                                tol = list(epstol = 1e-12, convtol = 1e-8)))
  beta               = fit.mr.ash$beta
  pip                = 1 - get_phi(fit.mr.ash)$phi[,1]

  return (list(fit = fit.mr.ash, t = t.mr.ash[3], beta = beta, pip = pip,
               rsse = norm(y.test - predict(fit.mr.ash, X.test), '2')))
}
