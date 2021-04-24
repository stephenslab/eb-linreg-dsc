#!/bin/bash
module load gcc/10.2.0
module load R/3.6.1

# http://www.diracprogram.org/doc/release-12/installation/mkl.html
#export NUMEXPR_NUM_THREADS=1
export OMP_NUM_THREADS=1
export MKL_SERVICE_FORCE_INTEL=1
export MKL_NUM_THREADS="28"
export MKL_DYNAMIC="FALSE"

dsc linreg.dsc --truncate --target all -c 28
