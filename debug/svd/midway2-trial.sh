#!/bin/bash
#SBATCH -p mstephens
#SBATCH --time=00:15:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=2
#SBATCH -o slurm-out/slurm-%j.out
#SBATCH -e slurm-out/slurm-%j.err
source ~/.bashrc
module load gcc/10.2.0
module load mkl/2020.up1
module load R/3.6.1
conda activate py39
export MKL_SERVICE_FORCE_INTEL=1
export OMP_NUM_THREADS=2
sos execute t1tde3279f6980946 -v 2 -s default
