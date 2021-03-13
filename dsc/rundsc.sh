#!/bin/bash

INPUT=${1}
PREV_OUTDIR="dsc_result"
if [ -d ${PREV_OUTDIR} ]; then rm -rf ${PREV_OUTDIR}; fi
rm -f ${PREV_OUTDIR}.html
python ~/Documents/work/dsc/main.py ${INPUT}
