from dsc.query_engine import Query_Processor as dscQP
from dsc import dsc_io
import pandas as pd
import numpy as np
import os

from pymir import pd_utils


def flex_read(filepath):
    rds = f"{filepath}.rds"
    pkl = f"{filepath}.pkl"
    res = None
    if os.path.isfile(rds) and os.path.isfile(pkl):
        print(f"{filepath}")
        print(f"Both rds and pkl DSC output files exist; files should be cleaned up by running \"dsc --clean\"")
    elif os.path.isfile(rds):
        res = dsc_io.load_dsc(rds)
    elif os.path.isfile(pkl):
        res = dsc_io.load_dsc(pkl)
    return res


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
        resdict    = flex_read(fitpath)
        datadict   = flex_read(simpath)
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

def changepoint_predictions(dsc_outdir, methods, order = 0, sfix = 1, dsc_iter = 1):
    dbpath     = os.path.join(dsc_outdir, os.path.basename(os.path.normpath(dsc_outdir)) + ".db")
    targets    = ["changepoint", "changepoint.basis_k", "changepoint.sfix", "fit_cpt", "predict_linear"]
    conditions = [f"changepoint.basis_k == {order}", f"changepoint.sfix == {sfix}"]
    groups     = ["fit:"]
    qp         = dscQP(dbpath, targets, conditions, groups)
    outdf      = pd_utils.select_dfrows(qp.output_table, [f"$(DSC) == {dsc_iter}"])
    ypred      = dict()
    b0pred     = dict()
    b1pred     = dict()
    simpath0   = os.path.join(dsc_outdir, outdf.loc[outdf.index[0], 'changepoint.output.file'])
    for method in methods:
        dfrow    = pd_utils.select_dfrows(outdf, [f"$(fit_cpt) == {method}"])
        assert (dfrow.index.shape[0] == 1), "Error! More than one row is selected."
        idx      = dfrow.index[0]
        fitpath  = os.path.join(dsc_outdir, dfrow.loc[idx, 'fit_cpt.output.file'])
        predpath = os.path.join(dsc_outdir, dfrow.loc[idx, 'predict_linear.output.file'])
        simpath  = os.path.join(dsc_outdir, dfrow.loc[idx, 'changepoint.output.file'])
        assert (simpath == simpath0), "Error! Different simulation file"
        pred     = flex_read(predpath)
        fit      = flex_read(fitpath)
        ypred[method]  = pred['yest']
        b1pred[method] = fit['beta_est']
        b0pred[method] = fit['intercept']
    data = flex_read(simpath0)
    X = data['X']
    y = data['y']
    beta = data['beta']
    Xtest = data['Xtest']
    ytest = data['ytest']
    se = data['se']
    return X, y, Xtest, ytest, beta, se, ypred, b0pred, b1pred
