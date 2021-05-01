# Large-scale multiple linear regression using DSC

Numerical experiments for evaluating the performance of [Mr. Ash](https://github.com/stephenslab/mr.ash.alpha) 
and other linear regression methods that are well suited for large-scale (possibly sparse) data sets. 
This is a reproduction, using [DSC](https://stephenslab.github.io/dsc-wiki/overview), 
of the [workflow](https://github.com/stephenslab/mr-ash-workflow) for the Mr.ASH manuscript by 
Kim, Wang, Carbonetto and Stephens (2020). See also [dsc-linreg](https://github.com/stephenslab/dsc-linreg).

The prediction errors of the different methods can be seen here: [Comparison of prediction errors](https://banskt.github.io/iridge-notes/2021/03/24/compare-prediction-accuracy-linear-regression-methods-dsc.html)

### Dependencies
Methods in the pipeline require external R packages, which can be installed using
```
install.packages(c("devtools", "ggplot2", "glmnet", "L0Learn", "BGLR", "ncvreg"))
devtools::install_github("stephenslab/susieR")
devtools::install_github("pcarbo/varbvs",subdir = "varbvs-R")
devtools::install_github("stephenslab/mr.ash.alpha")
devtools::install_github("stephenslab/ebmr.alpha")
```
The external python packages can be installed using
```
conda install --copy nose numpy scipy matplotlib pywavelets scikit-learn
git clone git@github.com:GAMPTeam/vampyre.git
cd vampyre
pip install -e .
pip install git+git://github.com/stephenslab/ebmrPy
```

Note: `vampyre` has some module dependency issues if I try to install it directly from github.

### How to run
```
cd dsc
dsc linreg.dsc --target [TARGET] --host [HOSTFILE]
```
[TARGET] can be `linreg` or `trendfilter`.

There are two [HOSTFILE]:
 - `gwdg.yml` for running on MPIBPC GWDG cluster
 - `midway2.yml` for running on UChicago RCC cluster

To check and debug
```
dsc linreg.dsc --truncate -o ../dsc_result_trial --host gwdg.yml
```
