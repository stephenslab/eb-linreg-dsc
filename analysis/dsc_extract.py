from dsc.query_engine import Query_Processor as dscQP
from dsc import dsc_io
import pandas as pd
import numpy as np
import os

from pymir import pd_utils

def emvamp_mse_hist(dsc_outdir, method, dim, sfrac, pve, rho):
    target     = ["simulate", "fit"]
    conditions = [f"simulate.sfrac == {sfrac}",
                  f"simulate.dims == '({dim[0]},{dim[1]})'",
                  f"simulate.pve == {pve}",
                  f"simulate.rho == {rho}"
                 ]
    groups     = None
    dbpath     = os.path.join(dsc_outdir, os.path.basename(os.path.normpath(dsc_outdir)) + ".db")
    allscores  = list()
    qp         = dscQP(dbpath, target, conditions, groups)
    outdf      = pd_utils.select_dfrows(qp.output_table, [f"$(fit) == {method}"])
    for idx in outdf.index.to_numpy():
        fitpath    = os.path.join(dsc_outdir, outdf.loc[idx, 'fit.output.file'])
        simpath    = os.path.join(dsc_outdir, outdf.loc[idx, 'simulate.output.file'])
        resdict    = dsc_io.load_dsc(fitpath + ".pkl")
        datadict   = dsc_io.load_dsc(simpath + ".pkl")
        bhat_hist  = resdict['model']
        Xtest      = datadict['Xtest']
        ytest      = datadict['ytest']
        se         = datadict['se']
        niter      = len(bhat_hist)
        scores     = np.zeros(niter)
        n, p       = Xtest.shape
        for it in range(niter):
            bhati  = bhat_hist[it]
            ypred  = np.dot(Xtest, bhati[1:]) + bhati[0]
            rmse   = np.sqrt(np.mean((ytest.reshape(n,1) - ypred)**2))
            scores[it] = rmse / se
        allscores.append(scores)
    return allscores
