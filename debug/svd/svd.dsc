DSC:
  python_modules: numpy
  output: dsc_result
  replicate: 1
  define:
    data: normalpy, normalR
  run: data * svd

normalpy: normal.py
  n:       500
  p:       200
  $X:      X

normalR: R(X <- matrix(0, n, p); X[,seq(1,p)] = rnorm(n * p))
  n:       500
  p:       200
  $X:      X

svd: R(s <- svd(X))
  X:    $X
  $out: s

dump: R(A <- X)
  X:    $X
  $A:   A
