#!/bin/bash

#DSC_CMD="python /home/saikat/Documents/work/dsc/main.py"
DSC_CMD="dsc"

case $1 in
    "append")
        ${DSC_CMD} linreg.dsc --target all -c 16 -s existing
        ;;
    "trial-append")
        ${DSC_CMD} linreg.dsc --target all --replicate 1 -c 16 -s existing -o trial
        ;;
    "trial-rerun")
        rm -rf trial trial.html
        ${DSC_CMD} linreg.dsc --target all --replicate 1 -c 16 -s none -o trial
        ;;
    *)
        ${DSC_CMD} "$@"
        ;;
esac
