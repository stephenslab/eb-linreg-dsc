# This R script implements the "lasso" module.
out <- fit_lasso(X, as.vector(y), cvlambda = "1se")

